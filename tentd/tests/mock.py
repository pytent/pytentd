"""Classes used for mocking"""

from __future__ import absolute_import

from collections import defaultdict
from weakref import proxy

class CallableAttribute(object):
    def __call__(self):
        return self.value

    def __set__(self, instance, value):
        self.value = value

class MockResponse(object):
    """A mock response, for use with MockFunction"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    #: Use a default status code
    status_code = 200

    #: The JSON method
    json = CallableAttribute()

class MockFunction(dict):
    """A callable argument->value dictionary for patching over a function"""

    def __init__(self, **kwargs):
        super(MockFunction, self).__init__(**kwargs)
        self.history = defaultdict(lambda: 0)

    def __call__(self, value, *args, **kwargs):
        """Return the value"""
        if value in self:
            self.history[value] += 1
            return self[value]
        raise KeyError("No mock response set for '{}'".format(value))

    def was_called(self, value):
        """Check if a value was called for"""
        return self.history[value] > 0

    def was_not_called(self, value):
        """Check if a value was not called for"""
        return self.history[value] == 0
    
    def __repr__(self):
        return "MockFunction{}".format(super(MockFunction, self).__repr__())
