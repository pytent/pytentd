"""Test cases for the follower document"""

from py.test import raises, mark

from tentd.documents import db, Follower

def test_updated_at(entity, follower):
    """Test that the follower updated_at time is changed on save"""
    first_updated_at = follower.updated_at
    
    follower.identity = "http://this.is.a.new.url.com"
    follower.save()

    assert first_updated_at != follower.updated_at != follower.created_at
