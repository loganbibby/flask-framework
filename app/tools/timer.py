from utils import get_timestamp

TIMERS = {}

def start(name=None):
    global TIMERS

    if name is None:
        name = 'timer-%s' % get_timestamp()

    TIMERS[name] = {
        'start': get_timestamp(),
        'active': True,
    }

    return name

def stop(name):
    global TIMERS

    if name not in TIMERS.keys():
        return None

    TIMERS[name]['stop'] = get_timestamp()
    TIMERS[name]['active'] = False
    TIMERS[name]['elapsed'] = TIMERS[name]['stop'] - TIMERS[name]['start']

    if TIMERS[name]['elapsed'] is None:
        return 0
    else:
        return TIMERS[name]['elapsed']

def stop_all():
    global TIMERS

    active_timers = []
    for name, this_timer in TIMERS.iteritems():
        if this_timer['active']:
            active_timers.append(name)

    for name in active_timers:
        stop(name)

    all_timers = []
    for name, this_timer in TIMERS.iteritems():
        all_timers.append( (name, this_timer['elapsed']) )

    return all_timers
