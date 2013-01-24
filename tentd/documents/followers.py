"""Followers and followings"""

__all__ = ['Follower', 'Following']

from datetime import datetime

from mongoengine import *

from tentd.documents import db, EntityMixin
from tentd.documents.auth import KeyPair
from tentd.utils import json_attributes, time_to_string
from tentd.utils.auth import generate_keypair

class Follower(EntityMixin, db.Document):
    """Someone following an Entity"""

    meta = {
        'allow_inheritance': False,
        'indexes': ['identity'],
    }

    #: The identity of the follower
    identity = URLField(unique_with='entity')

    #: The time the follower was created
    created_at = DateTimeField(default=datetime.now)

    permissions = None
    licenses = None
    types = None

    notification_path = StringField()

    #add link to keypair 
    keypair = ReferenceField('KeyPair', required=True)

    def __init__(self, **kwargs):
        super(Follower, self).__init__(**kwargs)

        if not self.keypair:
            keyid,key = generate_keypair()
            kp = KeyPair(mac_id=keyid, mac_key=key,
                            mac_algorithm="hmac-sha-256")
            kp.save()
            self.keypair = kp

        if not self.created_at:
            self.created_at = datetime.utcnow()

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

    meta = {
        'allow_inheritance': False,
        'indexes': ['identity'],
    }

    #: The identity of the following
    identity = URLField(unique_with='entity')

    #: The time the following was created
    created_at = DateTimeField(default=datetime.now)
