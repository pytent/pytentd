""" Test cases for the user profile data """

from tentd import db
from tentd.documents import Entity, CoreProfile, Post
from tentd.tests import TentdTestCase, EntityTentdTestCase

class EntityTest(EntityTentdTestCase):
    def test_create_entity(self):
        """Test creating and accessing an Entity"""
        assert self.entity == Entity.objects.get(name="testuser")

    def test_create_identical_entity(self):
        """Check that properly inserting a document does not overwrite an existing one"""
        with self.assertRaises(db.NotUniqueError):
            entity = Entity(name="testuser")
            entity.save()

class CoreProfileTest(TentdTestCase):
    def test_core_profile(self):
        self.entity = Entity(name="testuser")
        self.entity.save()

        with self.assertRaises(Exception):
            print self.entity.core

class DeletionTest(TentdTestCase):
    """Test cascading deletes"""

    def test_post_delete(self):
        self.entity = Entity(name="testuser").save()
        self.post = Post(
            entity=self.entity,
            schema="http://example.com/thisisnotrelevant",
            content={'a': 'b'}).save()

        assert self.post in Post.objects
        assert self.post in self.entity.posts
        
        self.entity.delete(safe=True)

        assert self.post not in Post.objects
