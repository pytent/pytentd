"""Tests for pytentd

Also provides some imports from the testing libraries used.
"""

__all__ = [
    'TestCase',
    'FlaskTestCase',
    'TentdTestCase',
    'EntityTentdTestCase']

from unittest import TestCase, skip
from collections import defaultdict
from weakref import proxy

from flask import json
from mock import Mock, patch
from werkzeug.datastructures import Headers

from tentd.lib.flask import cached_method
from tentd.lib.test import FlaskTestCase

from tentd import create_app
from tentd.documents import *

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
        headers = Headers()
        headers.extend(kwargs.pop('headers', {}))
        headers.set('Authorization', self.auth_header)
        return method(*args, headers=headers, **kwargs)

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

    data = None

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

    __objects = []

    def __init__(self, **kwargs):
        super(MockFunction, self).__init__(**kwargs)
        self.__objects.append(proxy(self))

    @classmethod
    def reset(cls):
        """Clear the history of all MockFunction objects"""
        for obj in cls.__objects:
            if hasattr(obj, '_history'):
                delattr(obj, '_history')

    @property
    def history(self):
        """Return the objects history, creating it if it does not exist"""
        if not hasattr(self, '_history'):
            self._history = defaultdict(lambda: 0)
        return self._history

    def __call__(self, argument, **kargs):
        """Return the value"""
        if argument in self:
            self.history[argument] += 1
            if 'data' in kargs:
                self[argument].data = kargs['data']
            return self[argument]
        raise KeyError("No mock response set for '{}'".format(argument))

    def assert_called(self, argument):
        assert self.history[argument] > 0

    def assert_called_only_once(self, argument):
        assert self.history[argument] == 1

    def assert_not_called(self, argument):
        assert self.history[argument] == 0

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            super(MockFunction, self).__repr__())

class TentdTestCase(FlaskTestCase):
    """A base test case for pytentd

    It handles setting up the app and request contexts

    As it uses the ``setUp`` and ``tearDown`` methods heavily, it makes
    equivalent functions available under the names ``before`` and ``after``,
    so that end users can avoid repeated calls to ``super()``. The class
    versions of these methods are ``beforeClass`` and ``afterClass``.
    """

    #: The default configuration for a testing app
    _default_configuration = {
        'DEBUG': True,
        'TESTING': True,
        'SERVER_NAME': 'tentd.example.com',
        'MONGODB_SETTINGS': {
            'db': 'tentd-testing',
        },
    }

    @classmethod
    def create_app(cls, config):
        return create_app(config)

    # Setup and teardown functions
    # These functions are listed in the order they are called in

    @classmethod
    def setUpClass(cls):
        """Place the app in testing mode and initialise the database"""
        super(TentdTestCase, cls).setUpClass(beforeClass=False)

        cls.app.client = cls.app.test_client()
        cls.app.secure_client = AuthorizedClientWrapper(cls.app.client)

        # Deprecated
        cls.client = cls.app.client
        cls.secure_client = cls.app.secure_client

        cls.beforeClass()

    def setUp(self, before=True):
        super(TentdTestCase, self).setUp(before=False)

        self.addCleanup(TentdTestCase.clear_database)
        self.addCleanup(MockFunction.reset)

        if before:
            self.before()

    # Other functions

    @staticmethod
    def clear_database():
        for collection in (Entity, Follower, Post, Profile, Group):
            collection.drop_collection()

class EntityTentdTestCase(TentdTestCase):
    """A test case that sets up an entity"""
    name = 'testuser'

    def setUp(self):
        super(EntityTentdTestCase, self).setUp(before=False)
        # TODO: Entity.add()
        self.entity = Entity(name=self.name).save()
        self.entity.create_core(
            identity= "http://example.com",
            servers=["http://tent.example.com"])

        self.before()

    def url_for(self, endpoint, **kwargs):
        """Calls url_for, using self.entity if needed"""
        single_user_mode = current_app.config.get('SINGLE_USER_MODE', None)
        if not single_user_mode and 'entity' not in kwargs:
            kwargs['entity'] = self.entity.name
        return super(EntityMixin, self).url_for(endpoint, **kwargs)

    __LINK_FORMAT = '<{}/profile>; rel="https://tent.io/rels/profile"'

    def assertEntityHeader(self, route):
        """Test that a route has the entity link header"""
        response = self.client.head(route)
        header = self.__LINK_FORMAT.format(self.base_url + self.name)
        assert response.headers['Link'] == header

class SingleUserTestCase(EntityTentdTestCase):
    name = 'singleuser'

    configuration = {
        'SINGLE_USER_MODE': name,
    }

if __name__ == '__main__':
    from unittest import TestLoader
    TestLoader().discover('.')
