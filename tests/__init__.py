""" Tests for pytentd """

from unittest import TestCase, main

from tentd import create_app, db

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
		cls.app = create_app()
		
	def setUp (self):
		"""	Set up a request context and create the db """
		self.ctx = self.app.test_request_context()
		self.ctx.push()
		
		db.create_all(app=self.app)
		
	def tearDown (self):
		""" Clear the database, and the current request """
		db.drop_all()
		self.ctx.pop()
