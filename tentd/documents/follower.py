"""Followers and followings"""

__all__ = ['Follower']

from datetime import datetime

from mongoengine import *
from mongoengine.signals import pre_save, post_save

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
    identity = URIField(required=True, unique_with='entity')

    #: The Server/API root of the follower
    servers = ListField(URIField(), required=True)

    #: The time the follower was created
    created_at = DateTimeField(required=True, default=datetime.now)

    #: The time the follower was last updated
    updated_at = DateTimeField(required=True, default=datetime.now)

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
        return {
            'id': str(self.id),
            'entity': self.identity,
            'servers': self.servers,
            'created_at': time_to_string(self.created_at),
            'updated_at': time_to_string(self.updated_at),
            'notification_path': self.notification_path,
            'permissions': self.permissions,
            'types': self.types,
            'licenses': self.licenses
        }

    @staticmethod
    def pre_save(sender, document, **kwargs):
        """Update the updated_at attribute"""
        document.updated_at = datetime.now()

post_save.connect(KeyPair.owner_post_save, sender=Follower)
pre_save.connect(Follower.pre_save, sender=Follower)
