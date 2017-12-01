from datetime import datetime, timedelta
import hashlib
import string
import random
from urlparse import urlparse, urljoin
from mongoengine.queryset.visitor import Q
from flask import request, g, flash, current_app, session, render_template
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_principal import Principal, Identity, identity_changed, identity_loaded,\
                            Permission, AnonymousIdentity, UserNeed
from app.model import *

class InvalidLoginError(Exception): pass

def process_logout():
    # Flask-Login
    logout_user()

    # Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

def process_login(username, password, remember=False, flash_=True):
    try:
        user = User.objects().get(username=username, deleted=None)

        if not user.check_password(password):
            raise InvalidLoginError()

    except (User.DoesNotExist, InvalidLoginError):
        login = Login()
        login.visitor = g.visitor
        login.username = username
        login.successful = False
        login.save()

        if flash_:
            flash('Login information incorrect', 'error')

        return False

    login_user(user, remember=remember)

    identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(str(user.id)))

    login = Login()
    login.visitor = g.visitor
    login.user = user
    login.successful = True
    login.save()

    user.sessions.append( login )
    user.save()

    current_app.logger.info('User login successful: %s - Log: %s' % (user.id, login.id))

    if flash_:
        flash('Login successful! Welcome, %s!' % user, 'success')
    return True

def check_email(email):
    users = User.objects( Q(deleted=None) & (Q(username=email) | Q(email=email)) )
    return False if len( users ) else True

def create_user(username, password, firstname, lastname, email, save=True):
    if not check_email(email):
        current_app.logger.error('User already exists: %s' % username)
        return False

    user = User()
    user.username = username
    user.password = password
    user.firstname = firstname
    user.lastname = lastname
    user.email = email
    user.settings['confirmation'] = hashlib.md5( '%s.%s' % (user.email, datetime.utcnow().strftime('%c')) ).hexdigest()

    user.save()
    current_app.logger.info('Created user: %s (%s)' % (user, user.id))

    if brand:
        brand.users.append( user )
        brand.save()
        current_app.logger.debug('Added user %s to brand: %s' % (user.id, brand.id))

        t = tasks.misc.enduser_welcome_email.delay( str(user.id) )
        current_app.logger.debug('Queued welcome email for %s: %s' % (user.id, t.id))

    return user

def change_email(user, email, save=True):
    if check_email(email):
        return False

    user.email = email

    if save:
        user.save()

    current_app.logger.info('Changed e-mail address for %s to %s' % (user.id, email))
    return True

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
    return None

def generate_password(size=8, inc_punctuation=True):
    chars = string.letters + string.digits

    if inc_punctuation:
        chars += string.punctuation

    return ''.join( (random.choice(chars)) for x in range(size) )

def passwordrecovery(user):
    recovery_confirm = hashlib.sha256( user.username ).hexdigest()
    recovery_expiry = datetime.utcnow() + timedelta(hours=48)

    user.settings['recovery_confirm'] = recovery_confirm
    user.settings['recovery_expiry'] = recovery_expiry
    user.save()
    current_app.logger.debug('Generated and saved password recovery token to user: %s' % user.id)

    recoveryurl = url_for('security.lostpass_confirm', confirm=user.get_setting('recovery_confirm'), external=True)

    sendmail(
        recipients=[user.email_recipient],
        subject='%s: Password recovery' % app.config['SITE_NAME'],
        body=render_template('emails/security.lostpass.html', recoveryurl=recoveryurl)
    )
