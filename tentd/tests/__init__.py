"""Tests for pytentd

Also provides some imports from the testing libraries used.
"""

__all__ = ['TentdTestCase', 'EntityTentdTestCase', 'skip']

from unittest import TestCase, skip

from flask import json, Response

from tentd import create_app
from tentd.documents import *
from tentd.tests.mocking import MockFunction

class TestResponse(Response):
    def json(self):
        if self.mimetype == 'application/json':
            if not hasattr(self, '_json'):
                self._json = json.loads(self.data)
            return self._json
        return None

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

        cls.clear_database()
        
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
        self.clear_database()
        MockFunction.reset()
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

        del cls.app
        del cls.client

    # Other functions

    @classmethod
    def clear_database(cls):
        for collection in (Entity, Follower, Post, Profile):
            collection.drop_collection()

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

class EntityTentdTestCase(TentdTestCase):
    """A test case that sets up an entity and it's core profile"""
    name = "testuser"
    
    def setUp(self):
        self.entity = Entity(name=self.name)
        self.entity.save()
        self.entity.create_core(
            identity= "http://example.com",
            servers=["http://tent.example.com"]
        )
        
        super(EntityTentdTestCase, self).setUp()

    def assertEntityHeader(self, route):
        """Assert that the route returns the correct header"""
        header = '<{}{}/profile>; rel="https://tent.io/rels/profile"'.format(
            self.base_url, self.name)
        
        self.assertEquals(self.client.head(route).headers['Link'], header)
