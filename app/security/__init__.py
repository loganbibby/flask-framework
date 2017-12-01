from datetime import datetime, timedelta
import hashlib
from urlparse import urlparse, urljoin
from flask import request, g, flash, current_app
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_principal import Principal, Identity, identity_changed, identity_loaded, UserNeed
from flask_principal import Permission
from app.model import *
from blueprint import bp

def init_app(app):
    # Setup LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'security.login'

    # Setup Principal
    principals = Principal(app)

    app.register_blueprint(bp) # User auth frontend

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user

        if current_user.is_authenticated:
            identity.provides.add(UserNeed(current_user.id))

            for group in current_user.securitygroups:
                for need in group.needs:
                    identity.provides.add( (need.type_, need.name) )

    @login_manager.user_loader
    def load_user(userid):
        return Users.objects().get(id=userid)

class Permissions:
    cache = {}

    def _get_permission(self, groupname):
        if groupname not in cache.keys():
            group = SecurityGroup.objects().get(name=groupname)
            cache[groupname] = group
        else:
            group = cache[groupname]

        needs = []
        for need in group.needs:
            needs.append( (need.type_, need.name) )

        return Permission(*needs)

    def require(self, groupname, http_exception=None):
        group = self._get_permission(groupname)
        return group.require(http_exception)

    def reverse(self, groupname):
        group = self._get_permission(groupname)
        return group.reverse()

    def allows(self, groupname, identity):
        group = self._get_permission(groupname)
        return group.allows(identity)

    def can(self, groupname):
        group = self._get_permission(groupname)
        return group.can()

permissions = Permissions()
