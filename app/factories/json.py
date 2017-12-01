import re
from flask.json import JSONEncoder, JSONDecoder
from bson.objectid import ObjectId

decode_re_pattern = re.compile( r'^<REPAT:(.+)>$' )

class JsonEncoder(JSONEncoder):
    def default(self, o):
        if type(o) == ObjectId:
            try:
                return str(o)
            except TypeError:
                pass
        elif isinstance(o, re._pattern_type):
            return '<REPAT:%s>' % o.pattern
        return JSONEncoder.default(self, o)

class JsonDecoder(JSONDecoder):
    def default(self, o):
        if o.startswith('<REPAT:'):
            match = decode_re_pattern.match(o)
            if match:
                return re.compile( match.group(1) )
        return JSONDecoder.default(self, o)

def init_app(app):
    app.json_encoder = JsonEncoder
    app.json_decoder = JsonDecoder
