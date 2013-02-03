"""Followers and followings"""

__all__ = ['Follower', 'Following']

from datetime import datetime

from mongoengine import *

from tentd.documents import db, EntityMixin
from tentd.documents.auth import KeyPair
from tentd.utils import json_attributes, time_to_string

from tentd.utils.auth import generate_keypair
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

    permissions = None
    licenses = None
    types = None

    notification_path = StringField()

    keypair = ReferenceField('KeyPair', required=True, dbref=False)

    def __init__(self, **kwargs):
        super(Follower, self).__init__(**kwargs)

        if self.keypair is None:
            keyid, key = generate_keypair()
            self.keypair = KeyPair(
                mac_id=keyid, mac_key=key, mac_algorithm="hmac-sha-256")
            self.keypair.save()

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
