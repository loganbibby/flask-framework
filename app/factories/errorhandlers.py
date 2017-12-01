from werkzeug.exceptions import *
from flask import render_template

def init_app(app):
    @app.errorhandler(BadRequest)
    @app.errorhandler(InternalServerError)
    @app.errorhandler(TooManyRequests)
    @app.errorhandler(RequestURITooLarge)
    @app.errorhandler(NotFound)
    @app.errorhandler(RequestTimeout)
    @app.errorhandler(MethodNotAllowed)
    @app.errorhandler(Forbidden)
    @app.errorhandler(Unauthorized)
    def error_generic(e):
        template_kwargs = {
            'errorcode':            e.code,
            'errorname':            e.name,
            'errordescription':     e.description
        }

        return render_template('error_generic.html', **template_kwargs)
