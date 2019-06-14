import re

REGISTRY = []

# avoid OOP at all costs
def match(regex):
    def regex_deco(action):
        def fu(message=None, user=None, *params):
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

def route(message, user):
    for regex, action in REGISTRY:
        params = [ p for p in re.findall(regex, message) if p ] 
        re.search(regex)
        if params:
            print("oddstring$$$ {} {} {} {}".format(action, message, user, params))
            values = action(message, user, *params)
            return values

