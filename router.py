import re
import logging
import json

from pprint import pformat

REGISTRY = []
DEFAULT = None
print("defult init")
print(DEFAULT)

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)

# avoid OOP at all costs
def match(regex, default=False):
    def regex_deco(action):
        # def fu(message=None, user=None, channel=None, *params):
        def fu(*args, **kwargs):
            return action(*args, **kwargs)
        # validate regex
        rx = validate_regex(regex)
        if rx:
            exec_pair = (rx, fu)
            REGISTRY.append(exec_pair)
            if default:
                # fail if 2 defaults exists
                # assert DEFAULT is None
                DEFAULT = exec_pair
        return fu
    return regex_deco


def validate_regex(regex):
    try:
        rx = re.compile(regex)
    except re.error:
        rx = None
    return rx

def route_action(regex, action, message, user, channel):
    m = re.search(regex, message)
    if m:
        params = m.groups()
        event = {
            'message': message,
            'user': user,
            'channel': channel,
            'params': params
            }
        values = action(bot_event=event)
        return values

def route(message, user, channel):
    for regex, action in REGISTRY:
        return route_action(regex, action, message, user, channel)
    if DEFAULT is not None:
        regex, action = DEFAULT
        return route_action(regex, action, message, user, channel)
#SECTION MOVED FROM CHATBOT

