import hashlib
from datetime import datetime
from mongoengine import *
from mongoengine import signals
from flask_login import UserMixin

class UsernameChangedWithoutRehashError(Exception): pass

class User(Document, UserMixin):
    active = BooleanField(default=True)
    username = StringField(required=True)
    password_ = StringField(db_field='password', required=True)
    firstname = StringField(required=True)
    lastname = StringField(required=True)
    email = EmailField(required=True)
    securitygroups = ListField( ReferenceField('SecurityGroup') )
    settings = DictField()
    sessions = ListField( ReferenceField('Login') )
    added = DateTimeField(required=True)
    updated = DateTimeField(required=True)
    deleted = DateTimeField()

    @property
    def email_recipient(self):
        return (str(self), self.email)

    @property
    def lastlogin(self):
        if len(self.sessions):
            return self.sessions[ len(self.sessions)-1 ]
        else:
            return None

    @property
    def email_verified(self):
        return self.get_setting('email_verified', False)

    @email_verified.setter
    def email_verified_set(self, value):
        self.settings['email_verified'] = value

    def get_setting(self, key, default=None):
        if key in self.settings.keys():
            return self.settings[key]
        return default

    def __str__(self):
        return '%s %s' % (self.firstname, self.lastname)

    def get_id(self):
        return str(self.id)

    def _generate_hash(self, ptp):
        salt = '%s.%s' % (self.username, ptp)
        hash_ = salt

        for i in range(0, 1000):
            hash_ = hashlib.sha256( '%s.%s' % (hash_, salt) ).hexdigest()

        return hash_

    def check_password(self, password):
        if self.password != self._generate_hash(password):
            return False
        return True

    @property
    def password(self):
        return self.password_

    @password.setter
    def password(self, ptp):
        self.password_ = self._generate_hash(ptp)

    def change_username(self, username, password):
        self.username = username
        self.password = password

    def clean(self, *args, **kwargs):
        if self.added is None:
            self.added = datetime.utcnow()
        self.updated = datetime.utcnow()

        updates, removals = self._delta()

        if 'username' in updates.keys() and 'password' not in updates.keys():
            raise UsernameChangedWithoutRehashError()
