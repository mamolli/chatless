import re

REGISTRY = []

# avoid OOP at all costs
def match(regex):
    def regex_deco(action):
        def fu(message=None, user=None):
            return action(message, user)
        # validate regex
        if validate_regex(regex):
            REGISTRY.append(regex, fu)
        return fu
    return regex_deco

@match('rego')
def out(message, user):
    print("out")
    return 1

def validate_regex(regex):
    try:
        re.compile(regex)
        valid = True
    except re.error:
        valid = False
    return valid

def route(message, user):
    for action in REGISTRY:

print(REGISTRY[0]())