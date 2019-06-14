
import router

def test_routing():
    @router.match('hi')
    def hi(message, user):
        print("out")
        return 1

    assert router.route("hi there", "me") == 1
    assert len(router.REGISTRY) == 1

def test_routing_params():
    @router.match('hello (\S+)')
    def hi2(message, user, param):
        print("out")
        return param

    assert router.route("hello there", "me") == "there"
    assert len(router.REGISTRY) == 2