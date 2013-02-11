"""Test the profile types"""

from mongoengine import NotUniqueError
from py.test import fixture, mark, raises

from tentd.documents.profiles import Profile, CoreProfile, GenericProfile

def test_profile_implementation():
    """Assert that Profile cannot be instantiated directly"""
    with raises(NotImplementedError):
        Profile()

def test_core_profile_schema(entity):
    assert entity.core.schema == CoreProfile.__schema__

def test_core_profile_json(entity):
    assert entity.core.to_json()['entity'] == "http://example.com"

def test_core_profile_data(entity):
    assert entity.core.identity == "http://example.com"

def test_core_profile_constraint(entity):
    """Test that multiple profiles with the same schema cannot be added"""
    with raises(Exception):
        CoreProfile(entity=entity, identity="http://bad.example.com").save()

@fixture
def generic_profile(request, entity):
    profile = GenericProfile(
        entity=entity,
        schema="https://tent.io/types/info/example/v0.0.0",
        content={
            'attr': 'value',
            'dict': {'attr': 'value'},
            'list': [1, 2, 3],
        })
    request.addfinalizer(profile.delete)
    return profile.save()

def test_attributes(generic_profile):
    assert generic_profile.content['dict']['attr'] == 'value'

def test_json_attributes(generic_profile):
    assert generic_profile.to_json()['content']['dict']['attr'] == 'value'

def test_unique_schema(entity, generic_profile):
    with raises(NotUniqueError):
        GenericProfile(entity=entity, schema=generic_profile.schema).save()
