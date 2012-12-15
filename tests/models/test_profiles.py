"""Test the profile types"""

import tests

from sqlalchemy.exc import IntegrityError

from tentd import db
from tentd.models.entity import Entity
from tentd.models.profiles import Core

class CoreTest (tests.AppTestCase):
    def before (self):
        self.entity = Entity(name="test", core={
            'identifier': "http://example.com",
        })
        self.commit(self.entity)

    def test_schema(self):
        assert self.entity.core.schema == Core.__schema__

    def test_autocreate_arguments(self):
        assert self.entity.core.identifier == "http://example.com"

    def test_profile_constraint(self):
        """Test that multiple profiles with the same schema cannot be added"""
        entity = Entity(name="testuser", core=None)
        self.commit(entity)
        with self.assertRaises(IntegrityError):
            self.commit(Core(entity=entity, identifier="http://1.example.com"))
            self.commit(Core(entity=entity, identifier="http://2.example.com"))
