from datetime import datetime
from mongoengine import *
from mongoengine import signals
from app.tools.choices import *

class SecurityNeed(Document):
    meta = {
        'indexes': [
            {'fields': ('name', 'type_'), 'unique': True}
        ]
    }

    display_name = StringField(required=True)
    description = StringField(required=True)
    name = StringField(required=True)
    type_ = StringField(db_field='type', required=True, choices=security_need_types)
    added = DateTimeField(required=True)
    updated = DateTimeField(required=True)
    deleted = DateTimeField()

    def __str__(self):
        return self.display_name

    def clean(self):
        if self.added is None:
            self.added = datetime.utcnow()
        self.updated = datetime.utcnow()
