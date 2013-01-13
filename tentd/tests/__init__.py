"""Tests for pytentd

Also provides some imports from the testing libraries used.
"""

__all__ = ['TentdTestCase', 'MockResponse', 'MockFunction', 'patch' 'skip']

from unittest import TestCase, skip

from flask import json, jsonify, Response, _request_ctx_stack
from mock import NonCallableMock, patch
from werkzeug import cached_property

from tentd import create_app, db

class TestResponse(Response):
    @cached_property
    def json(self):
        if self.mimetype == 'application/json':
            return json.loads(self.data)
        return None

class MockResponse(NonCallableMock):
    """A mock response, for use with MockFunction"""

    #: Use a default status code
    status_code = 200

    #: The argument the response is for
    __argument__ = None

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

    def __call__(self, argument):
        """Return the value, setting it's __argument__ attribute"""
        if argument in self:
            self[argument].__argument__ = argument
            return self[argument]
        raise KeyError("No mock response set for '{}'".format(argument))

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            super(MockFunction, self).__repr__())

class TentdTestCase(TestCase):
    """A base test case for pytentd

    It handles setting up the app and request contexts
    
    As it uses the ``setUp`` and ``tearDown`` methods heavily, it makes 
    equivalent functions available under the names ``before`` and ``after``, so
    that end users can avoid repeated calls to ``super()``. The class versions
    of these methods are ``beforeClass`` and ``afterClass``.
    """

    dbname = 'tentd-testing'

    # Setup and teardown functions
    # These functions are listed in the order they are called in
    
    @classmethod
    def setUpClass(cls):
        """Place the app in testing mode and initialise the database"""
        config = {
            'DEBUG': True,
            'TESTING': True,
            'SERVER_NAME': 'tentd.example.com',
            'MONGODB_SETTINGS': {'db': cls.dbname},
        }
        
        cls.app = create_app(config)
        cls.app.response_class = TestResponse
        cls.client = cls.app.test_client()

        cls.beforeClass()

    @classmethod
    def beforeClass(cls):
        pass
        
    def setUp(self):
        """ Create the database, and set up a request context """
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.before()
        
    def before(self):
        pass
    
    def after(self):
        pass
    
    def tearDown(self):
        """Clear the database, and the current request"""
        self.after()
        for collection in db.connection[self.dbname].collection_names():
            if not collection == 'system.indexes':
                db.connection[self.dbname].drop_collection(collection)
        try:
            self.ctx.pop()
        except:
            pass
    
    @classmethod
    def afterClass(cls):
        pass

    @classmethod
    def tearDownClass (cls):
        cls.afterClass()

    # Other functions

    @property
    def base_url(self):
        return 'http://' + self.app.config['SERVER_NAME'] + '/'

    def assertStatus(self, response, status):
        """Asserts that the response has returned a certain status code"""
        try:
            self.assertIn(response.status_code, status)
        except TypeError:
            self.assertEquals(response.status_code, status)

    def assertJSONError(self, response):
        self.assertIn('error', response.json())
