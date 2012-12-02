""" Tests for pytentd """

from os import close, remove
from tempfile import mkstemp
from unittest import TestCase, main

from flask import Response, json_available, json
from werkzeug import cached_property

from tentd import create_app, db

class TestResponse (Response):
	@cached_property
	def json (self):
		if not json_available:
			raise NotImplementedError
		elif not self.mimetype == 'application/json':
			return None
		return json.loads(self.data)

class AppTestCase (TestCase):
	"""
	A base test case for pytentd.
	It handles setting up the app and request contexts
	"""
	
	@classmethod
	def setUpClass (cls):
		"""
		Place the app in testing mode (allowing exceptions to propagate,
		and initialise the database
		"""
		cls.db_fd, cls.db_filename = mkstemp()
		
		config = {
			'DEBUG': True,
			'TESTING': True,
			'SQLALCHEMY_DATABASE_URI': "sqlite:///" + cls.db_filename
		}
		
		cls.app = create_app(config)
		cls.app.response_class = TestResponse
		cls.client = cls.app.test_client()
		
	def setUp (self):
		"""	Create the database, and set up a request context """
		self.ctx = self.app.test_request_context()
		self.ctx.push()
		
		db.create_all(app=self.app)
		
	def tearDown (self):
		""" Clear the database, and the current request """
		db.drop_all()
		self.ctx.pop()

	@classmethod
	def tearDownClass (cls):
		"""	Close the database file, and delete it """
		close(cls.db_fd) 
		remove(cls.db_filename)

	def assertStatus (self, response, status):
		try:
			self.assertIn(response.status_code, status)
		except TypeError:
			self.assertEquals(response.status_code, status)
