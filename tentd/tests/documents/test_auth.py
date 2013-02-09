""" Test cases for the user profile data """

from py.test import fixture, raises, mark

from tentd.documents import db, Follower
from tentd.documents.auth import generate_id, generate_key, KeyPair

def test_generate():
    assert generate_id()
    assert generate_key()

def test_keypair_defaults():
    """Test that KeyPair uses sensible defaults"""
    kp = KeyPair()
    assert kp.mac_id and isinstance(kp.mac_id, basestring)
    assert kp.mac_key and isinstance(kp.mac_key, basestring)
    assert kp.mac_algorithm and isinstance(kp.mac_algorithm, basestring)

def test_follower_keypair_property(follower):
    """Test that the property works and a KeyPair has been generated"""
    assert isinstance(follower.keypair, KeyPair)

def test_follower_cascading_delete(follower):
    """Test that the KeyPair is deleted with the follower"""
    assert KeyPair.objects.get(owner=follower)

    follower.delete()

    with raises(KeyPair.DoesNotExist):
        KeyPair.objects.get(owner=follower)
