"""Tests for pytentd"""

from os import close, remove
from tempfile import mkstemp
from unittest import TestCase, main

from flask import Response, json_available, json, Flask, make_response, jsonify
from werkzeug import cached_property

from tentd import create_app, db

class TestResponse(Response):
    @cached_property
    def json(self):
        if not json_available:
            raise NotImplementedError
        elif not self.mimetype == 'application/json':
            return None
        return json.loads(self.data)

class AppTestCase(TestCase):
    """A base test case for pytentd

    It handles setting up the app and request contexts
    
    As it uses the ``setUp`` and ``tearDown`` methods heavily, it makes 
    equivalent functions available under the names ``before`` and ``after``, so
    that end users can avoid repeated calls to ``super()``. The class versions
    of these methods are ``beforeClass`` and ``afterClass``.
    """

    # Setup and teardown functions
    # These functions are listed in the order they are called in
    
    @classmethod
    def setUpClass(cls):
        """Place the app in testing mode and initialise the database"""
        cls.db_fd, cls.db_filename = mkstemp()
        
        config = {
            'DEBUG': True,
            'TESTING': True,
            'SERVER_NAME': 'tentd.example.com',
            'SQLALCHEMY_DATABASE_URI': "sqlite:///" + cls.db_filename
        }
        
        cls.app = create_app(config)
        cls.app.response_class = TestResponse
        cls.client = cls.app.test_client()

        external_config = {
            'SERVER_NAME': 'localhost:5000'
        }

        cls.external_app = cls.mock_app(external_config)
        
        cls.beforeClass()
    
    @classmethod
    def mock_app(cls, config):
        """ Creates a mock app which simulates our pytentd server. 

        This should probably be externalised to another class. And possibly 
        made into a real pytentd server rather than just a mocked one. However 
        this works for now. """

        # Create a basic flask mock
        mock = Flask('testing')
        mock.config['SERVER_NAME'] = config['SERVER_NAME']

        # Create routes for it.
        @mock.route('/testuser', methods=['HEAD'])
        def entity_header():
            """ Returns a hardcoded link to the entity_profile route. """
            resp = make_response()
            resp.headers['Link'] = '<{0}>; rel="{1}"'.format(
                'http://localhost:5000/testuser/profile', 
                'https://tent.io/rels/profile')
            return resp

        @mock.route('/testuser/profile', methods=['GET'])
        def entity_profile():
            """ Returns a hardcoded JSON which points to itself. """
            return jsonify({"https://tent.io/types/info/core/v0.1.0": {
                "licences": [], 
                    "servers": [
                        "http://pytentd.alexanderdbrown.com/testuser"
                    ], 
                    "tent_version": "0.2", 
                    "entity": "http://localhost:5000/testuser"
                }
            }), 200

        @mock.route('/testuser/notification', methods=['GET'])
        def notify():
            """ Returns with OK. It shouldn't need anything else. """
            return 'OK', 200

        return mock

    @classmethod
    def beforeClass(cls):
        pass
        
    def setUp(self):
        """ Create the database, and set up a request context """
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        
        db.create_all(app=self.app)
        
        self.before()
        
    def before(self):
        pass
    
    def after(self):
        pass
    
    def tearDown(self):
        """Clear the database, and the current request"""
        self.after()
        db.drop_all()
        try:
            self.ctx.pop()
        except:
            pass
    
    @classmethod
    def afterClass(cls):
        pass

    @classmethod
    def tearDownClass (cls):
        """Close the database file, and delete it"""
        cls.afterClass()
        close(cls.db_fd) 
        remove(cls.db_filename)

    # Other functions

    @property
    def base_url(self):
        return 'http://' + self.app.config['SERVER_NAME'] + '/'

    @property
    def external_base_url(self):
        return 'http://' + self.external_app.config['SERVER_NAME'] + '/'
        
    def commit(self, *objects):
        """Commit several objects to the database"""
        for o in objects:
            db.session.add(o)
        db.session.commit()

    def assertStatus(self, response, status):
        """Asserts that the response has returned a certain status code"""
        try:
            self.assertIn(response.status_code, status)
        except TypeError:
            self.assertEquals(response.status_code, status)

    def assertJSONError(self, response):
        self.assertIn('error', response.json)
