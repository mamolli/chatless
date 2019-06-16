
import router

def test_routing():
    @router.match('hi')
    def hi(bot_event):
        print("out")
        return 1

    assert router.route("hi there", "chan", "me") == 1
    assert len(router.REGISTRY) == 1

def test_routing_params():
    @router.match(r'hello (\S+)')
    def hi2(bot_event):
        print("out")
        return bot_event['params'][0]

    assert router.route("hello there", "chann", "me") == "there"
    assert len(router.REGISTRY) == 2

def test_routing_params_default():
    @router.match(r'hello (\S+)')
    def hi2(bot_event):
        print("out")
        return bot_event['params'][0]

    @router.match(r'(\S+)', default=True)
    def hi2(bot_event):
        print("out")
        return bot_event['params'][0]

    assert router.route("hello there", "chann", "me") == "there"
    assert router.route("something", "chann", "me") == "something"
    assert len(router.REGISTRY) == 4