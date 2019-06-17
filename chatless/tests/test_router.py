import re
import pytest
from chatless import router

def setup_function():
    router.REGISTRY = []

def test_routing():
    @router.match('hi')
    def _(bot_event):
        return 1

    assert router.route("hi there", "chan", "me") == 1
    assert len(router.REGISTRY) == 1

def test_routing_params():
    @router.match(r'hello (\S+)')
    def _(bot_event):
        return bot_event['params'][0]

    assert router.route("hello there", "chann", "me") == "there"
    assert len(router.REGISTRY) == 1

def test_malformed():
    with pytest.raises(TypeError):
        @router.match(231)
        def _(bot_event):
            return bot_event['params'][0]

def test_routing_params_default():
    @router.match(r'hello (\S+)')
    def _(bot_event):
        return bot_event['params'][0]

    @router.default
    @router.match(r'nothing')
    def _(bot_event):
        return bot_event['message']

    assert router.route("hello there", "chann", "me") == "there"
    assert router.route("something", "chann", "me") == "something"
    assert router.route("nothing", "chann", "me") == "nothing"
    assert len(router.REGISTRY) == 2
