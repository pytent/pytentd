from json import loads

from tests import AppTestCase, main

from tentd import db
from tentd.models.entity import Entity

class EntityBlueprintTest (AppTestCase):
	def setUp (self):
		super(EntityBlueprintTest, self).setUp()
		self.user = Entity(name="testuser")
		db.session.add(self.user)
		db.session.commit()

	def test_entity_link (self):
		r = self.client.head("/testuser/")
		self.assertIn("/testuser/profile", r.headers['Link'])

	def test_entity_profile_json (self):
		r = self.client.get("/testuser/profile")
		
		self.assertEquals(r.mimetype, 'application/json')
		self.assertIn('https://tent.io/types/info/core/v0.1.0', r.json)

if __name__ == "__main__":
    main()
