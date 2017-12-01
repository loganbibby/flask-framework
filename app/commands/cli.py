import os
import click
from flask.cli import FlaskGroup

def create_the_app(info):
    from app import create_app
    return create_app('command')

@click.group(cls=FlaskGroup, create_app=create_the_app)
def cli():
    pass
