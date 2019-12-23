import re
import logging

REGISTRY = []
DEFAULT_FUNCTION = None

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)

def default(action):
    def fu(*args, **kwargs):
        return action(*args, **kwargs)
    # hate this so much, however it is cleanest apraoch atm
    global DEFAULT_FUNCTION
    DEFAULT_FUNCTION = fu
    return fu

def match(regex):
    def regex_deco(action):
        def fu(*args, **kwargs):
            return action(*args, **kwargs)
        # validate regex
        rx = re.compile(regex)
        exec_pair = (rx, fu)
        register(exec_pair)
        return fu
    return regex_deco

def register(exec_pair):
    log.debug("Registering pattern-matching function %s", exec_pair)
    REGISTRY.append(exec_pair)

def route(message, user, channel):
    values = None
    for regex, action in REGISTRY:
        log.debug("Pattern-matching message %s with regexp %s", message, regex)
        m = re.search(regex, message) if regex is not None else None
        if m:
            params = m.groups()
            event = create_bot_event(message, user, channel, params)
            values = action(bot_event=event)
    # when no values found
    if DEFAULT_FUNCTION is not None and values is None:
        event = create_bot_event(message, user, channel)
        values = DEFAULT_FUNCTION(bot_event=event)
    return values

def create_bot_event(message, user, channel, params=None):
    event = {
        'message': message,
        'user': user,
        'channel': channel,
        'params': params
    }
    return event
