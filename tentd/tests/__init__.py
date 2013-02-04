"""Tests for pytentd

Also provides some imports from the testing libraries used.
"""

__all__ = ['TentdTestCase', 'EntityTentdTestCase', 'skip']

from unittest import TestCase, skip

from flask import json, Response

from werkzeug.datastructures import Headers

from tentd import create_app
from tentd.documents import *
from tentd.tests.mocking import MockFunction

class TestResponse(Response):
    def json(self):
        if self.mimetype == 'application/json':
            if not hasattr(self, '_json'):
                self._json = json.loads(self.data)
            return self._json
        raise Exception("Response has no json data")

class AuthorizedClientWrapper:
    """Provide an authorized wrapper around the Werkzeug test client
    
    Given an existing tent test client and a KeyPair object, this
    object emulates HMAC requests and provides transparent access to
    the real test client's GET, POST, PUT, HEAD and DELETE methods
    """


    macid  = "s:f5949a1d"
    tstamp = 1355181298
    nonce  = "b07235"
    mac    = "swgy4RpdIBaFpA1hmAbZrph24VVg9FwmJgMm9GkgiLE="
    keypair = None

    def __init__(self, tentclient):
        self._client = tentclient

    @property
    def auth_header(self):
        return 'MAC id="{0}",ts="{1}",nonce="{2}",mac="{3}"'.format(
            self.macid, self.tstamp, self.nonce, self.mac)

    def get(self, *args, **kwargs):
        return self._exec(self._client.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._exec(self._client.post, *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._exec(self._client.put, *args, **kwargs)

    def head(self, *args, **kwargs):
        return self._exec(self._client.head, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._exec(self._client.delete, *args, **kwargs)

    def _exec(self, method, *args, **kwargs):
    
        h = Headers()

        if(kwargs.has_key('headers')):
            h.extend(kwargs['headers'])
        
        h.set('Authorization',self.auth_header)

        kwargs['headers'] = h
    
        return method(*args,**kwargs)


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
    def setUpClass(cls, config=dict()):
        """Place the app in testing mode and initialise the database"""
        configuration = {
            'DEBUG': True,
            'TESTING': True,
            'SERVER_NAME': 'tentd.example.com',
            'MONGODB_SETTINGS': {'db': cls.dbname},
        }

        if config:
            configuration.update(config)
        
        cls.app = create_app(configuration)
        cls.app.response_class = TestResponse
        cls.client = cls.app.test_client()

        #set up authorized client
        cls.secure_client = AuthorizedClientWrapper(cls.client)

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
        for collection in (KeyPair, Entity, Follower, Post, Profile, Group):
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

    @staticmethod
    def json_error_response(response):
        return 'error' in response.json()

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

    LINK_FORMAT = '<{}/profile>; rel="https://tent.io/rels/profile"'

    def assertEntityHeader(self, route):
        """Assert that the route provides the link header"""
        response = self.client.head(route)
        self.assertIn('Link', response.headers)
        self.assertEquals(
            response.headers['Link'],
            self.LINK_FORMAT.format(self.base_url + self.name))

class SingleUserTestCase(EntityTentdTestCase):    
    @classmethod
    def setUpClass(cls):
        super(SingleUserTestCase, cls).setUpClass(config={
            'SINGLE_USER_MODE': cls.name,
        })
