""" Test cases for the user profile data """

from tests import AppTestCase, main

from tentd import db
from tentd.models.entity import Entity, Server, CoreProfile
		
class EntityTest (AppTestCase):
	@classmethod
	def setUpClass (cls):
		super(EntityTest, cls).setUpClass()
		
		cls.entity = Entity(name="testuser")
	
	def test_create_entity (self):
		db.session.add(self.entity)

		queried_entity = Entity.query.filter_by(name=self.entity.name).first()

		return self.entity is queried_entity
		
class CoreProfileTest (AppTestCase):
	@classmethod
	def setUpClass (cls):
		super(CoreProfileTest, cls).setUpClass()
		
		cls.entity = Entity(name="test", core={
			'identifier': "http://example.com",
		})
		
	def test_autocreate (self):
		self.assertIsInstance(self.entity.core, CoreProfile)
	
	def test_autocreate_arguments (self):
		self.assertEqual(self.entity.core.identifier, "http://example.com")

class ServerTest (AppTestCase):
	def setUp (self):
		super(ServerTest, self).setUp()
		
		self.entity = Entity(name="testuser")
		self.ident1 = Server("http://example.com/abc", core=self.entity.core)
		self.ident2 = Server("http://example.com/def", core=self.entity.core)
		
		for obj in (self.entity, self.ident1, self.ident2):
			db.session.add(obj)
		db.session.commit()
	
	def test_server_in_identifiers (self):
		self.assertIn(self.ident1, self.entity.core.servers)
		self.assertIn(self.ident2, self.entity.core.servers)
		
if __name__ == "__main__":
    main()
