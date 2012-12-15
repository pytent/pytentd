from json import loads

from tests import AppTestCase, main

from tentd import db
from tentd.models.entity import Entity

class EntityBlueprintTest (AppTestCase):
	def setUp (self):
		super(EntityBlueprintTest, self).setUp()
		self.name = 'testuser'
		self.expected_api_root = 'http://localhost/' + self.name
		self.expected_link_header = '<{0}/profile>; rel="https://tent.io/rels/profile"'.format(self.expected_api_root)
		
		self.user = Entity(name=self.name)
		db.session.add(self.user)
		db.session.commit()

	def test_entity_link (self):
		r = self.client.head('/' + self.name)
		self.assertEquals(r.headers['Link'], self.expected_link_header)
	
	def test_entity_link_404 (self):
		self.assertStatus(self.client.head('/non-existent-user'), 404)
	
	def test_entity_profile_404 (self):
		self.assertStatus(self.client.head('/non-existent-user/profile'), 404)
	
	def test_entity_profile_json (self):
		r = self.client.get('/testuser/profile')
		
		self.assertEquals(r.mimetype, 'application/json')
		self.assertIn('https://tent.io/types/info/core/v0.1.0', r.json)
		
	def test_entity_core_profile (self):
		r = self.client.get('/testuser/profile')
		url = r.json['https://tent.io/types/info/core/v0.1.0']['entity']
		self.assertEquals(url, self.expected_api_root)
