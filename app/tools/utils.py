import calendar
import time
import os
import sys
import bson

def is_windows_os():
    if os.name == 'nt':
        return True
    return False

def get_timestamp():
    return calendar.timegm( time.gmtime() )

def set_secret_key(app, filename='secret_key'):
    if 'SECRET_KEY_FILE' in app.config:
        filename = app.config['SECRET_KEY_FILE']

    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print '*** No secret key file. Create it with:'

        if not os.path.isdir(os.path.dirname(filename)):
            print 'mkdir -p ', os.path.dirname(filename)

        print 'head -c 24 /dev/urandom >', filename

        sys.exit(1)

def search_tuples(list_of_tuples, search, reverse=False):
    results = [v[1 if not reverse else 0] for i, v in enumerate(list_of_tuples) if v[0 if not reverse else 1] == search]
    if len(results) > 0:
        return results[0]
    else:
        return None

def convert_choice(value, choices_name, reverse=False):
    import stello.choices as choices

    if hasattr(choices, choices_name):
        result = search_tuples( getattr(choices, choices_name), value, reverse )

    return result if result is not None else False

def check_dict(dict_, key):
    if key in dict_.keys():
        return dict_[key]
    return False

def listdiff(first, second):
    second = set(second)
    return [i for i in first if i not in second]

def pretty_printer(obj, spaces=2, printlines=True):
    lines = []

    if type(obj) == bson.son.SON:
        obj = obj.to_dict()

    sorted_keys = sorted( obj.keys() )

    for key in sorted_keys:
        value = obj[key]

        def print_line(line, linespaces):
            lines.append( '%s%s' % (linespaces*' ', line) )

        try:
            if type(value) == dict:
                print_line('- %s:' % key, spaces)
                lines += pretty_printer(value, spaces+2)
            elif type(value) == list:
                if len(value) > 0:
                    print_line('- %s: [' % key, spaces)
                    for item in value:
                        if type(item) == dict:
                            lines += pretty_printer(item, spaces+6)
                        else:
                            print_line('%s, '% item, spaces+4)
                    print_line(']', spaces+2)
                else:
                    print_line('- %s: []' % key, spaces)
            else:
                print_line('- %s: %s' % (key, value), spaces)
        except Exception as e:
            print ' !!!! Cannot process %s: %s' % (key, e)

    if printlines:
        for line in lines:
            print line
    else:
        return lines

def allowed_extension(filename, allowed=[]):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed
