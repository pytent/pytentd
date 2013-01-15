"""Mock classes"""

from collections import defaultdict

from mock import Mock, patch

class CallableAttribute(object):
    """An attribute that can be called to retrieve the data,
    throwing an exception if it has not been set"""
    def __init__(self, error_message, exception_class=Exception):
        self.exception_class = exception_class
        self.error_message = error_message
    
    def __call__(self):
        try:
            return self.data
        except AttributeError:
            raise self.exception_class(self.error_message)

    def __set__(self, instance, value):
        self.data = value

class MockResponse(Mock):
    """A mock response, for use with MockFunction"""

    #: Use a default status code
    status_code = 200

    #: The json data for the response
    json = CallableAttribute(error_message="No json data has been set")
    
    def __str__(self):
        return "<MockResponse for {}>".format(self.__argument__)

class MockFunction(dict):
    """A callable argument->value dictionary for patching over a function

    New argument->value pairs can be assigned in the same way as a dict,
    and values can be returned by calling it as a function.

        with mock.patch('requests.head', new_callable=MockFunction) as head:
            head['http://example.com'] = MockResponse(data="Hello world.")
            ...
    """

    def __init__(self, **kwargs):
        self.update(kwargs)
        self.history = defaultdict(lambda: 0)

    def __call__(self, argument):
        """Return the value"""
        if argument in self:
            self.history[argument] += 1
            return self[argument]
        raise KeyError("No mock response set for '{}'".format(argument))

    def assert_called(self, argument):
        assert self.history[argument] > 0

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            super(MockFunction, self).__repr__())