""" Test cases for the user profile data """

from unittest import TestCase, main

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
		
		cls.url = "http://example.com/profile/jamesravencroft"
		cls.entity = Entity(url=cls.url)
		
	def test_create_entity (self):
		db.session.add(self.entity)

		queried_entity = Entity.query.filter_by(url=self.url).first()

		return self.entity is queried_entity

if __name__ == "__main__":
    main()
