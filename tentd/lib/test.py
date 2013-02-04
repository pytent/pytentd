"""Flask test framework"""

from __future__ import absolute_import

from unittest import TestCase

from flask import Config

class FlaskTestCase(TestCase):
    _default_configuration = {
        'DEBUG': True,
        'TESTING': True,
    }

    configuration = {}

    @classmethod
    def create_app(cls, config):
        return NotImplementedError("Must implement create_app()")

    @property
    def base_url(self):
        return 'http://' + self.app.config['SERVER_NAME'] + '/'

    @classmethod
    def setUpClass(cls, beforeClass=True):
        """Place the app in testing mode and initialise the database"""
        config = dict()
        config.update(cls._default_configuration)
        config.update(cls.configuration)

        cls.app = cls.create_app(config)

        if beforeClass:
            cls.beforeClass()

    @classmethod
    def beforeClass(cls):
        pass

    def setUp(self, before=True):
        """Setup a response context"""
        self.ctx = self.app.test_request_context()
        self.ctx.push()

        if before:
            self.before()

    def before(self):
        """An extension of setUp, allowing tests to create data"""
        pass

    def tearDown(self):
        """Clear the current request"""
        self.ctx.pop()

    def assertStatus(self, response, status):
        """Asserts that the response has returned a certain status code"""
        try:
            self.assertIn(response.status_code, status)
        except TypeError:
            self.assertEquals(response.status_code, status)

    def assertJSONError(self, response):
        self.assertIn('error', response.json())
