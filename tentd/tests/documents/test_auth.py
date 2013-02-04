""" Test cases for the user profile data """

from tentd.documents import db, Follower
from tentd.documents.auth import generate_id, generate_key, KeyPair
from tentd.tests import EntityTentdTestCase

class KeyPairTest(EntityTentdTestCase):
    def test_generate(self):
        assert generate_id()
        assert generate_key()

    def test_keypair_defaults(self):
        keypair = KeyPair()

        assert keypair.mac_id
        assert keypair.mac_key
        assert keypair.mac_algorithm

        print type(keypair.mac_id)
        
        assert isinstance(keypair.mac_id, basestring)
        assert isinstance(keypair.mac_key, basestring)
        assert isinstance(keypair.mac_algorithm, basestring)

    def test_cascading_delete(self):
        keypair = KeyPair().save()
        
        follower = Follower(
            entity=self.entity, keypair=keypair,
            identity='http://example.com').save()

        assert follower.keypair is keypair

        print KeyPair.objects.get(mac_id=keypair.mac_id)

        keypair.delete()
        follower.delete()

        with self.assertRaises(KeyPair.DoesNotExist):
            print KeyPair.objects.get(mac_id=keypair.mac_id)
