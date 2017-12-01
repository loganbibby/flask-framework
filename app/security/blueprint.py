import hashlib
from datetime import datetime, timedelta
import pprint
from urlparse import urlparse, urljoin
# 3rd party
from flask import request, flash, redirect, url_for, render_template, session,\
                  abort, Blueprint, json, jsonify, current_app
from flask_login import login_required
from flask_principal import AnonymousIdentity
# Local
from app.tools import *
from app.model import *
from app.security.tools import *
from app.security.forms import *

bp = Blueprint('security', __name__, template_folder='templates')
returnurl_skey = 'security_returnurl'

def set_returnurl():
    if returnurl_skey not in session.keys():
        session[returnurl_skey] = get_redirect_target()
        if session[returnurl_skey] is None:
            if g.brand.type_ == 's':
                session[returnurl_skey] = url_for('propfront.index')
            elif g.brand.type_ == 'c':
                session[returnurl_skey] = url_for('crm.index')
            else:
                session[returnurl_skey] = url_for('security.login')

        current_app.logger.debug('Return URL set in %s: %s' % (request.endpoint, session[returnurl_skey]))
    else:
        current_app.logger.debug('At %s, return url already set to %s' % (request.endpoint, session[returnurl_skey]))

def get_returnurl():
    if returnurl_skey not in session.keys():
        return None
        current_app.logger.debug('No return url set')

    returnurl = session[returnurl_skey]
    current_app.logger.debug('return url set as %s' % returnurl)
    del session[returnurl_skey]
    return returnurl

@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.values)

    set_returnurl()

    if form.validate_on_submit():
        login_ = process_login(form.username.data, form.password.data, form.remember.data)

        if login_:
            if g.brand == current_user.primarybrand:
                return redirect( get_returnurl() )
            else:
                redirect_ = redirect(current_user.primarybrand.url)
                process_logout()
                current_app.logger.warn('Wrong brand for user %s: %s' % (current_user.get_id(), g.brand.id))
                flash('An error occurred while logging you in. Please login again.', 'error')
                return redirect_

    return render_template('security.login.html', form=form)

@bp.route("/register", methods=['GET', 'POST'])
def register():
    form = UserRegisterForm(request.values)

    if form.validate_on_submit():
        user = create_user(
            form.email.data,
            form.password.data,
            form.firstname.data,
            form.lastname.data,
            form.email.data,
            g.brand,
            save=False
            )

        if not user:
            flash('Looks like you already have an account. Login below.')
            return redirect( url_for('.login') )

        user.save()

        process_login(user.username, form.password.data, flash_=False)
        flash('Your user has been created! Check your e-mail to confirm your account.')

        returnurl = get_returnurl()
        nextendpoint = g.brand.get_setting('registration_nextendpoint')

        return redirect( url_for(nextendpoint) if nextendpoint is not None else returnurl )

    set_returnurl()

    return render_template('security.register.html', form=form)

@bp.route("/logout")
@login_required
def logout():
    process_logout()

    flash('You have been logged out.')

    return redirect( url_for('.login') )

@bp.route("/lostpassword", methods=['GET', 'POST'])
def lostpass():
    form = LostPassForm(request.values)

    if form.validate_on_submit():
        try:
            user = User.objects().get(username=form.username.data)
            passwordrecovery(user)
        except User.DoesNotExist:
            current_app.logger.debug('User does not exist')

        flash('If your account exists, you have been e-mailed a recovery link.')
        return redirect( url_for('.login') )

    return render_template('security.lostpass.html', form=form)

@bp.route("/lostpassword/<confirm>", methods=['GET', 'POST'])
def lostpass_confirm(confirm):
    try:
        user = User.objects().get(
            settings__recovery_confirm=confirm,
            settings__recovery_expiry__gte=datetime.utcnow()
        )
    except User.DoesNotExist:
        flash('This recovery link has already been used, expired, or is incorrect. Try the forgotten password utility again.')
        return redirect( url_for('.login') )

    form = PasswordChangeForm(request.values)

    if form.validate_on_submit():
        user.change_password( form.password.data )
        del user.settings['recovery_confirm']
        del user.settings['recovery_expiry']
        user.save()

        flash('Your password has been changed. Log in below.')

        return redirect( url_for('.login') )

    return render_template('security.lostpass_confirm.html', form=form, confirm=confirm)

@bp.route("/confirm/<confirm>")
def confirm(confirm):
    try:
        user = User.objects().get(settings__confirmid=confirm)
    except User.DoesNotExist:
        current_app.logger.error('Confirmation not found: %s - Visitor: %s' % (confirm, g.visitor.id))
        raise abort(404)

    del user.settings['confirmid']
    user.settings['confirmed'] = True
    user.save()

    flash('Thanks for confirming your e-mail! Please login below.')
    return redirect( url_for('security.login') )

@bp.route("/user_setting/<key>")
@login_required
def get_user_setting(key):
    return jsonify({'value': current_user.get_setting(key, False)})

@bp.route("/user_setting/<key>", methods=['POST'])
@login_required
def set_user_setting(key):
    key = key.lower()
    value = request.values.get('value')

    updateable_settings = {
        r'^intro_seen_': {
            'coerse': bool,
            'default': False,
            'store_default_on_coerse_error': True,
            'write_once': True
        }
    }

    updateable_setting = None

    for pattern, settings in updateable_settings.iteritems():
        if re.match(pattern, key):
            updateable_setting = settings
            break

    if not updateable_setting:
        return jsonify({'error': 'Cannot update user setting from API'}), 401

    try:
        value = updateable_setting['coerse']( value )
    except:
        if updateable_setting['store_default_on_coerse_error']:
            value = updateable_setting['default']
        else:
            return jsonify({'error': 'Improperly formatted value'}), 400

    if key in current_user.settings.keys() and updateable_setting['write_once']:
        return jsonify({'error': 'User setting already exists and is write-once'}), 400

    user = current_user._get_current_object()
    user.settings[key] = value
    user.save()

    return jsonify({'success': 'Changed user setting'})
