REGISTRY = []

# avoid OOP at all costs
def match(regex):
    def regex_deco(action):
        def fu(message=None, user=None):
            return action(message, user)
        return fu
    return regex_deco

@match('rego')
def out(message, user):
    print("out")
    return 1

print(out(2, 3))