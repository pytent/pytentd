""" Test cases for the user profile data """

import tests

from tentd import db
from tentd.models.entity import Entity
from tentd.models.profiles import CoreProfile
        
class EntityTest (tests.AppTestCase):
    def before (self):
        self.entity = Entity(name="testuser")
        self.commit(self.entity)
        
    def test_create_entity(self):
        entity = Entity.query.filter_by(name="testuser").one()
        assert self.entity is entity

    def test_autocreate_core (self):
        self.assertIsInstance(self.entity.core, CoreProfile)
