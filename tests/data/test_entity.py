""" Test cases for the user profile data """

from unittest import TestCase

from tentd import app, db
from tentd.models.entity import Entity

class DataTest (TestCase):
	@classmethod
	def setUpClass (cls):
		"""
		Place the app in testing mode (allowing exceptions to propagate,
		and initialise the database
		"""
		db.create_all()
		
		cls.entity = Entity(name="James Ravenscroft")
		
	def test_create_entity (self):
		db.session.add(self.entity)

		queried_entity = Entity.query.filter_by(name="James Ravenscroft").first()

		return self.entity is queried_entity

if __name__ == "__main__":
    unittest.main()
