import urlparse
from datetime import datetime
from flask import request, session, g
from flask_login import current_user
from mongoengine.queryset.visitor import Q
from app.model import Visitor

def init_app(app):
    @app.before_request
    def track_visitor():
        if request.blueprint in [None, 'static']:
            return

        if not app.config['MONGODB_ENABLE']:
            return

        visitor = None
        if 'visitorid' in session:
            try:
                visitor = Visitor.objects().get(session['visitorid'])
            except Visitor.DoesNotExist:
                app.logger.warn('Visitor does not exist: %s' % session['visitorid'])

        ipaddr = '127.0.0.1'
        if 'X-Real-IP' in request.headers.keys():
            ipaddr = request.headers['X-Real-IP']
        elif 'RemoteAddr' in request.headers.keys():
            ipaddr = request.headers['RemoteAddr']

        if visitor is None:
            visitor = Visitor()
            visitor.domain = request.headers['HOST']
            visitor.ipaddr_entered = ipaddr
            visitor.pageview_first = datetime.utcnow()
            app.logger.debug('New visitor')

        visitor.ipaddr_last = ipaddr
        visitor.browser = request.environ['HTTP_USER_AGENT']
        visitor.pageview_last = datetime.utcnow()

        if 'HTTP_ACCEPT_LANGUAGE' in request.environ.keys():
            visitor.httplang = request.environ['HTTP_ACCEPT_LANGUAGE'].split(',')[0]
        else:
            visitor.httplang = 'none'

        if visitor.ipaddr_last not in visitor.ipaddrs:
            visitor.ipaddrs.append( visitor.ipaddr_last )

        pageview = {}
        pageview['endpoint'] = request.endpoint
        pageview['fullpath'] = request.full_path
        pageview['method'] = request.method
        pageview['timestamp'] = datetime.utcnow()
        visitor.pageviews.create(**pageview)

        visitor.save()
        session['visitorid'] = str(visitor.id)
        g.visitor = visitor

        app.logger.debug('Visitor tracked: %s - IP: %s - Browser: %s' % (visitor.id, visitor.ipaddr_last, visitor.browser))

    @app.before_request
    def show_request():
        config_key = 'SHOW_REQUEST'
        if config_key not in app.config.keys() or not app.config[config_key]:
            return

        if not len(request.values.keys()):
            print 'No request values available'
            return

        msg = "Request values:\n"

        for key, value in request.values.iteritems():
            msg += " * %s: %s\n" % (key, value)

        print msg

    @app.before_request
    def set_referer():
        referer = request.headers.get('referer')
        if referer is not None:
            referer = urlparse.urlparse( referer )
        g.referer_parsed = referer
