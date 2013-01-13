""" Test cases for the user profile data """

from tentd import db
from tentd.models.entity import Entity
from tentd.tests import TentdTestCase

class EntityTest(TentdTestCase):
    def before(self):
        self.entity = Entity(name="testuser")
        self.entity.save()
        
    def test_create_entity(self):
        """Test creating and accessing an Entity"""
        assert self.entity == Entity.objects.get(name="testuser")
        assert Entity(name="testuser") == Entity.objects.get(name="testuser")

    def test_create_identical_entity(self):
        """Check that properly inserting a document does not overwrite an
        existing one"""
        with self.assertRaises(db.NotUniqueError):
            entity = Entity(name="testuser", test="boom")
            entity.save(force_insert=True)
