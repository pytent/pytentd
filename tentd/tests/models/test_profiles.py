"""Test the profile types"""

from mongoengine import NotUniqueError

from tentd import db
from tentd.models.entity import Entity
from tentd.models.profiles import Profile, CoreProfile, GenericProfile
from tentd.tests import TentdTestCase, EntityTentdTestCase

class ProfileTest(TentdTestCase):
    def test_no_profile(self):
        with self.assertRaises(NotImplementedError):
            Profile()

class CoreProfileTest(EntityTentdTestCase):
    def test_schema(self):
        assert self.entity.core.schema == CoreProfile.__schema__

    def test_json(self):
        assert 'entity' in self.entity.core.to_json()

    def test_arguments(self):
        assert self.entity.core.identity == "http://example.com"

    def test_profile_constraint(self):
        """Test that multiple profiles with the same schema cannot be added"""
        with self.assertRaises(Exception):
            CoreProfile(
                entity=self.entity,
                identity="http://bad.example.com"
            ).save()

class GenericProfileTest(EntityTentdTestCase):    
    def before(self):
        super(GenericProfileTest, self).before()
        
        self.profile = GenericProfile(
            entity=self.entity,
            schema="https://tent.io/types/info/example/v0.0.0",
            content={
                'attr': 'value',
                'dict': {'attr': 'value'},
                'list': [1, 2, 3],
            })
        self.profile.save()

    def test_attributes(self):
        assert self.profile.content['dict']['attr'] == 'value'

    def test_json_attributes(self):
        profile = Profile.objects.get(id=self.profile.id)
        assert profile.to_json()['content']['dict']['attr'] == 'value'

    def test_unique_schema(self):
        with self.assertRaises(NotUniqueError):
            GenericProfile(
                entity=self.entity,
                schema="https://tent.io/types/info/example/v0.0.0").save()
