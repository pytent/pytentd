""" Test cases for the user profile data """

from tentd.documents import db, Follower
from tentd.documents.auth import generate_id, generate_key, KeyPair
from tentd.tests import TestCase, EntityTentdTestCase

class KeyPairTest(TestCase):
    def test_generate(self):
        assert generate_id()
        assert generate_key()

    def test_keypair_defaults(self):
        keypair = KeyPair()

        assert isinstance(keypair.mac_id, basestring)
        assert isinstance(keypair.mac_key, basestring)
        assert isinstance(keypair.mac_algorithm, basestring)

class FollowerKeyPairTest(EntityTentdTestCase):
    def before(self):
        self.follower = Follower(
            entity=self.entity,
            identity='http://example.com')

        self.follower.save()

    def test_follower_keypair_property(self):
        """Test that the property works and a KeyPair has been generated"""
        assert self.follower.keypair

    def test_cascading_delete(self):
        """Test that the KeyPair is deleted with the follower"""
        assert KeyPair.objects.get(owner=self.follower)

        self.follower.delete()

        with self.assertRaises(KeyPair.DoesNotExist):
            KeyPair.objects.get(owner=self.follower)
