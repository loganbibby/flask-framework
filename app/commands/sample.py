import click
from cli import cli

@cli.group()
def sample():
    pass

@sample.command()
def command():
    click.echo('This is a sample group command!')
