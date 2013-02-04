""" Test cases for the user profile data """

from tentd.documents import db, Follower, KeyPair
from tentd.tests import EntityTentdTestCase

class KeyPairTest(EntityTentdTestCase):
    def test_cascading_delete(self):
        assert not KeyPair.objects.all()
        
        follower = Follower(
            entity=self.entity, identity='http://example.com').save()
        keypair = KeyPair(
            owner=follower,
            mac_id='<testid>',
            mac_key='',
            mac_algorithm='').save()
        assert keypair.owner == follower

        follower.delete()

        with self.assertRaises(KeyPair.DoesNotExist):
            KeyPair.objects.get(mac_id='<testid>')
