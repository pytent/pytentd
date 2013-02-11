"""Classes used for mocking"""

from __future__ import absolute_import

from collections import defaultdict
from weakref import proxy

from mock import Mock

class CallableAttribute(object):
    def __call__(self):
        return self.value

    def __set__(self, instance, value):
        self.value = value

class MockResponse(Mock):
    """A mock response, for use with MockFunction"""

    #: Use a default status code
    status_code = 200

    #: The JSON method
    json = CallableAttribute()

class MockFunction(dict):
    """A callable argument->value dictionary for patching over a function

    New argument->value pairs can be assigned in the same way as a dict,
    and values can be returned by calling it as a function.

        with mock.patch('requests.head', new_callable=MockFunction) as head:
            head['http://example.com'] = MockResponse(data="Hello world.")
            ...
    """

    __objects = []

    @classmethod
    def reset(cls):
        """Clear the history of all MockFunction objects"""
        for obj in cls.__objects:
            obj.history.clear()

    def __init__(self, **kwargs):
        super(MockFunction, self).__init__(**kwargs)
        self.__objects.append(proxy(self))
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
        return "MockFunction({})".format(
            super(MockFunction, self).__repr__())
