""" Test cases for the user profile data """

from tests import AppTestCase, main

from tentd import db
from tentd.models.entity import Entity
		
class DataTest (AppTestCase):
	@classmethod
	def setUpClass (cls):
		super(DataTest, cls).setUpClass()
		cls.url = "http://example.com/profile/jamesravencroft"
		cls.entity = Entity(url=cls.url)
	
	def test_create_entity (self):
		db.session.add(self.entity)

		queried_entity = Entity.query.filter_by(url=self.url).first()

		return self.entity is queried_entity

if __name__ == "__main__":
    main()
