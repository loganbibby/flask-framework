from datetime import datetime
from mongoengine import *

class Login(Document):
    meta = {'collection': 'log_login'}

    visitor = ReferenceField('Visitor', required=True)
    user = ReferenceField('User')
    username = StringField()
    successful = BooleanField(default=True)
    timestamp = DateTimeField(required=True)

    def clean(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

        if self.user and self.username:
            raise ValidationError('Login log must have either a string username or a User reference.')

        if self.successful and not self.user:
            raise ValidationError('Successful login log must have a User reference')

        if not self.successful and not self.username:
            raise ValidationError('Unsuccessful login log must have a string username')
