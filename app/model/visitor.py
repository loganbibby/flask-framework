from datetime import datetime
from mongoengine import *
from mongoengine import signals

class Pageview(EmbeddedDocument):
    endpoint = StringField()
    fullpath = StringField()
    method = StringField(required=True)
    timestamp = DateTimeField(required=True)

    @classmethod
    def set_timestamp(cls, sender, document, **kwargs):
        if document.timestamp is None:
            document.timestamp = datetime.utcnow()

class Visitor(Document):
    domain = StringField(required=True)
    browser = StringField(required=True)
    httplang = StringField(required=True)
    ipaddr_entered = StringField(required=True)
    ipaddr_last = StringField(required=True)
    ipaddrs = ListField(required=True, default=[])
    pageviews = EmbeddedDocumentListField(Pageview)
    pageview_first = DateTimeField(required=True)
    pageview_last = DateTimeField(required=True)
    updated = DateTimeField(required=True)
    added = DateTimeField(required=True)

    def clean(self):
        if self.added is None:
            self.added = datetime.utcnow()
        self.updated = datetime.utcnow()
