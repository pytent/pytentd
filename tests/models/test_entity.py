""" Test cases for the user profile data """

from tests import AppTestCase, main

from tentd import db
from tentd.models.entity import Entity
		
class EntityTest (AppTestCase):
	@classmethod
	def setUpClass (cls):
		super(EntityTest, cls).setUpClass()
		
		cls.entity = Entity(name="testuser")
	
	def test_create_entity (self):
		db.session.add(self.entity)

		queried_entity = Entity.query.filter_by(name=self.entity.name).first()

		return self.entity is queried_entity

if __name__ == "__main__":
    main()
