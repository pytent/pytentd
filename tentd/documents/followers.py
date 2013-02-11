"""Followers and followings"""

__all__ = ['Follower', 'Following']

from datetime import datetime

from mongoengine import *
from mongoengine.signals import post_save

from tentd.documents import db, EntityMixin, KeyPair
from tentd.utils import json_attributes, time_to_string

from tentd.lib.mongoengine import URIField

class Follower(EntityMixin, db.Document):
    """Someone following an Entity"""

    meta = {
        'allow_inheritance': False,
        'indexes': ['identity'],
    }

    #: The identity of the follower
    identity = URIField(unique_with='entity')

    #: The time the follower was created
    created_at = DateTimeField(default=datetime.now)

    #: The time the follower was last updated
    updated_at = DateTimeField(default=datetime.now)

    notification_path = StringField(required=True)
    
    permissions = None
    licenses = None
    types = None

    @property
    def keypair(self):
        return KeyPair.objects.get(owner=self)

    def __repr__(self):
        return "<Follower: {}>".format(self.identity)

    def to_json(self):
        return json_attributes(self,
           ('id', str),
            'identity',
           ('created_at', time_to_string),
            'notification_path',
            'permissions',
            'types',
            'licenses')

post_save.connect(KeyPair.owner_post_save, sender=Follower)

class Following(EntityMixin, db.Document):
    """An entity that a local entity is following"""

    meta = {
        'allow_inheritance': False,
        'indexes': ['identity'],
    }

    #: The identity of the following
    identity = URIField(unique_with='entity')

    #: The time the following was created
    created_at = DateTimeField(default=datetime.now)
