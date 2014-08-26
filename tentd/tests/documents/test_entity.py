""" Test cases for the user profile data """

from py.test import raises, mark

from tentd.documents import db, Entity, Post

def test_create_identical_entity(entity):
    """Test that we cannot create two entities with the same name"""
    with raises((db.NotUniqueError, db.OperationError)):
        Entity(name=entity.name).save()

def test_core_profile(app):
    """Assert that a core profile is created"""
    assert Entity(name="test").save().core is not None

def test_cascading_deletion(app):
    entity = Entity(name="test_cascading_deletion").save()
    post = Post.new(
        entity=entity, content={'a': 'b'},
        schema="http://example.com/thisisnotrelevant").save()

    assert post in Post.objects
    assert post in entity.posts

    entity.delete()

    assert post not in Post.objects
    assert post not in entity.posts
