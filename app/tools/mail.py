import requests
from flask import current_app
from utils import *

def sendmail(**kwargs):
    required_fields = [
        'recipients',
        'subject',
        'bodyHTML'
    ]
    list_required = [
        'recipients',
        'cc',
        'bcc'
    ]

    required_missing = listdiff(required_fields, kwargs.keys())
    if len(required_missing):
        return KeyError('Missing required fields: %s' % ', '.join(required_missing))

    list_required_missing = [k for k, v in kwargs.iteritems() if k in list_required and type(v) != list]
    if len(list_required_missing):
        return ValueError('List required for these fields: %s' % ', '.join(list_required_missing))

    if 'sender' not in kwargs.keys():
        kwargs['sender'] = current_app.config['MAIL_SENDER']

    headers = {
        'x-api-key': current_app.config['MAIL_APIKEY'],
    }
    r = requests.post( current_app.config['MAIL_URL'], headers=headers, json=kwargs )

    if r.status_code == 200:
        current_app.logger.debug('Successfully sent e-mail to %s with subject "%s"' % (','.join(kwargs['recipients']), kwargs['subject']))
        return True
    else:
        current_app.logger.error('Unable to send e-mail to %s with subject "%s": [%s] %s' % (','.join(kwargs['recipients']), kwargs['subject'], r.status_code, r.text) )
        for k, v in kwargs.iteritems():
            current_app.logger.debug('* %s: %s' % (k, v))
        return False
