""" Test cases for the user profile data """

from tentd import db
from tentd.models.entity import Entity
from tentd.models.profiles import CoreProfile
from tentd.tests import TentdTestCase, EntityTentdTestCase

class EntityTest(EntityTentdTestCase):
    def test_create_entity(self):
        """Test creating and accessing an Entity"""
        assert self.entity == Entity.objects.get(name="testuser")

    def test_create_identical_entity(self):
        """Check that properly inserting a document does not overwrite an
        existing one"""
        with self.assertRaises(db.NotUniqueError):
            entity = Entity(name="testuser")
            entity.save()

def CoreProfileTest(TentdTestCase):
    def test_core_profile(self):
        self.entity = Entity(name="testuser")
        self.entity.save()
        
        with self.assertRaises(Exception):
            core = self.entity.core
