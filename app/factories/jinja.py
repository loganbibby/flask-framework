import os
from datetime import datetime
import locale
from flask import current_app
from jinja2 import ChoiceLoader, FileSystemLoader
from markdown import markdown
from app.tools import convert_choice

def convert_timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp)

def format_datetime(date_, format='%m/%d/%Y', inputfmt=None):
    if type(date_) != datetime:
        if inputfmt is None:
            inputfmt = '%a, %d %b %Y %H:%M:%S GMT'
        date_ = datetime.strptime( date_, inputfmt )

    try:
        return date_.strftime(format)
    except ValueError as e:
        current_app.warn('Invalid datetime format: %s' % format)
        return date_.strftime('%m/%d/%Y')

def format_currency(value, grouping=True, decimals=True):
    if type(value) <> float:
        try:
            value = float(value)
        except:
            value = 0.0

    value = locale.currency(value, grouping=grouping)

    if not decimals:
        value = value[:-3]

    return value

def format_number(value, grouping=True):
    if type(value) <> int or type(value) <> float:
        try:
            value = float(value)
        except:
            value = 0.0

    return locale.format('%d', value, grouping=grouping)

def format_relative_days(days):
    if days == 0:
        return 'today'
    elif days < 30:
        return '%d days' % days
    elif days < 90:
        return '%d weeks' % round(days / 7, 0)
    else:
        return '%d months' % round(days / 30, 0)

def compare_datetime_to_now(value):
    if type(value) != datetime:
        raise ValueError('Value must be insantiated from datetime: %s' % type(value))
    return datetime.utcnow()-value

def filter_relative_days_from_now(value, ago=False):
    if type(value) != datetime:
        raise ValueError('Value must be insantiated from datetime: %s' % type(value))
    return_value = format_relative_days( compare_datetime_to_now(value).days )
    if ago:
        return '%s ago' % return_value if return_value != 'today' else return_value
    else:
        return return_value

def filter_markdown(value, **kwargs):
    if 'output_format' not in kwargs.keys():
        kwargs['output_format'] = 'html5'
    return markdown(value, **kwargs)

def is_dict(value):
    if type(value) == dict:
        return True
    else:
        return False

def init_app(app):
    # Override the Jinja2 loader to include
    # shared template files in its search path
    security_templates = os.path.join( app.config['ROOTDIR'], 'security/templates' )
    jinja_loader = ChoiceLoader([
        app.jinja_loader,
        FileSystemLoader([security_templates])
    ])
    app.jinja_loader = jinja_loader

    app.jinja_env.tests['dict'] = is_dict
    app.jinja_env.globals.update(compare_to_now=compare_datetime_to_now)
    app.jinja_env.filters['convert_choice'] = convert_choice
    app.jinja_env.filters['markdown'] = filter_markdown
    app.jinja_env.filters['relative_days_from_now'] = filter_relative_days_from_now
    app.jinja_env.filters['relative_days'] = format_relative_days
    app.jinja_env.filters['number'] = format_number
    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['format_date'] = format_datetime
    app.jinja_env.filters['from_timestamp'] = convert_timestamp_to_datetime

    @app.context_processor
    def inject():
        return { 'now': datetime.utcnow() }
