
import router

def test_routing():
    @router.match('hi')
    def hi(message, user, channel):
        print("out")
        return 1

    assert router.route("hi there", "chan", "me") == 1
    assert len(router.REGISTRY) == 1

def test_routing_params():
    @router.match(r'hello (\S+)')
    def hi2(message, user, channel, param):
        print("out")
        return param

    assert router.route("hello there", "chann", "me") == "there"
    assert len(router.REGISTRY) == 2