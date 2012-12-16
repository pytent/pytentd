"""Test the profile types"""

import tests

from sqlalchemy.exc import IntegrityError

from tentd import db
from tentd.models.entity import Entity
from tentd.models.profiles import Profile, CoreProfile, GenericProfile

class ProfileTest(tests.AppTestCase):
    def test_no_profile(self):
        with self.assertRaises(NotImplementedError):
            Profile()

class CoreTest(tests.AppTestCase):
    def before(self):
        self.entity = Entity(name="test", core={
            'identifier': "http://example.com",
        })
        self.commit(self.entity)

    def test_schema(self):
        assert self.entity.core.schema == CoreProfile.__schema__

    def test_json(self):
        assert 'entity' in self.entity.core.to_json()

    def test_arguments(self):
        assert self.entity.core.identifier == "http://example.com"

    def test_profile_constraint(self):
        """Test that multiple profiles with the same schema cannot be added"""
        entity = Entity(name="testuser", core=None)
        self.commit(entity)
        with self.assertRaises(IntegrityError):
            self.commit(CoreProfile(entity=entity))
            self.commit(CoreProfile(entity=entity))

class GenericTest(tests.AppTestCase):
    """This also tests tentd.utils.types.JSONDict"""
    
    def before(self):
        self.entity = Entity(name="test")
        self.profile = GenericProfile(
            entity=self.entity,
            schema="https://tent.io/types/info/example/v0.0.0",
            content={
                'attr': 'value',
                'dict': {'attr': 'value'},
                'list': [1, 2, 3],
            })
        self.commit(self.entity, self.profile)

    def test_attributes(self):
        assert self.profile.content['attr'] == 'value'

    def test_json(self):
        assert 'attr' in self.profile.to_json()

    def test_unique_schema(self):
        with self.assertRaises(IntegrityError):
            self.commit(GenericProfile(
                entity=self.entity,
                schema="https://tent.io/types/info/example/v0.0.0"))

    def test_mutable(self):
        self.profile.content['attr'] = 'newvalue'
        assert self.profile in db.session.dirty

    def test_mutable_subkey(self):
        """The top level of a JSONDict column is mutable, but any dictionaries
        below it are of type dict(), and changes to them will not mark the
        column as dirty: this needs to be done manually"""
        self.profile.content['dict']['attr'] = 'newvalue'
        self.profile.content['list'].append(4)
        self.profile.content.changed()
        assert self.profile in db.session.dirty
