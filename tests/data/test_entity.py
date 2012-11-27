""" Test cases for the user profile data """

import unittest

from tentd.data import db
from tentd.data.entity import Entity

class DataTest(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		db.create_all()
		
		self.entity = Entity(name="James Ravenscroft")
		
	@classmethod
	def test_create_entity(self):
		db.session.add(self.entity)
		db.session.commit()

		queried_entity = Entity.query.filter_by(name="James Ravenscroft").first()

		return self.entity is queried_entity

if __name__ == "__main__":
    unittest.main()
