import re

REGISTRY = []

# avoid OOP at all costs
def match(regex):
    def regex_deco(action):
        def fu(message=None, user=None, channel=None, *params):
            return action(message, user, *params)
        # validate regex
        rx = validate_regex(regex)
        if rx:
            exec_pair = (rx, fu)
            REGISTRY.append(exec_pair)
        return fu
    return regex_deco


def validate_regex(regex):
    try:
        rx = re.compile(regex)
    except re.error:
        rx = None
    return rx

def route(message, user, channel):
    for regex, action in REGISTRY:
        m = re.search(regex, message)
        if m:
            params = m.groups()
            values = action(message, user, channel, *params)
            return values

