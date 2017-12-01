from datetime import datetime
from mongoengine import *
from mongoengine import signals

class SecurityGroup(Document):
    display_name = StringField(required=True)
    name = StringField(required=True)
    description = StringField(required=True)
    needs = ListField( ReferenceField('SecurityNeed') )
    added = DateTimeField(required=True)
    updated = DateTimeField(required=True)
    deleted = DateTimeField()

    def __str__(self):
        return self.display_name

    def clean(self):
        if self.added is None:
            self.added = datetime.utcnow()
        self.updated = datetime.utcnow()
