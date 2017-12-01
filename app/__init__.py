import logging
import os
import locale
# 3rd party
from flask import Flask, g
from flask_login import LoginManager
from flask_session import Session
from celery import Celery
import mongoengine
from pymongo import MongoClient
# local
from app.factories import *
from app import security, tools

def create_app(name=None, config=None):
    rt = tools.timer.start()

    if name is None:
        name = 'mainapp'

    app = Flask(name, root_path=os.path.dirname(__file__))

    locale.setlocale( locale.LC_ALL, '' )

    app.config.from_object('app.config')

    if config:
        app.config.update( config )

    # Logger configuration
    logger.init_app(app)

    # Set secret key
    tools.set_secret_key(app)

    # JSON
    json.init_app(app)

    if app.debug:
        app.logger.debug('Application is in DEBUG mode.')

    if app.config['CELERY_ENABLE']:
        # Setup Celery
        app.config['CELERY_BROKER_URL'] = "amqp://%s:%s@%s/%s" % (
            app.config['RABBITMQ_USER'], app.config['RABBITMQ_PASS'],
            app.config['RABBITMQ_HOST'], app.config['RABBITMQ_VHOST'])
        app.config['CELERY_RESULT_BACKEND'] = "redis://%s:%s/1" % (
            app.config['REDIS_HOST'], app.config['REDIS_PORT'])

    # Setup MongoDB
    if app.config['MONGODB_ENABLE']:
        mongoengine.connect(
            alias='default',
            db=app.config['MONGODB_DB'],
            host=app.config['MONGODB_HOST'],
            connect=False
        )

    # Setup sessions
    if app.config['SESSION_ENABLE']:
        app.config['SESSION_MONGODB'] = MongoClient(host=app.config['MONGODB_HOST'])
        app.config['SESSION_MONGODB_DB'] = app.config['MONGODB_DB']
        Session(app)

    # Security
    security.init_app(app)

    # HTTP error handlers
    errorhandlers.init_app(app)

    # Jinja functions
    jinja.init_app(app)

    # Flask custom helpers
    prerequest.init_app(app)

    # bring it all together
    import blueprints # Import late
    app.register_blueprint(blueprints.sample) # Sample

    app.logger.debug('Completed initialization of %s app in %ds' % (app.name, tools.timer.stop(rt)) )

    return app
