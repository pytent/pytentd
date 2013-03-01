"""Followers and followings"""

__all__ = ['Follower', 'Following']

from datetime import datetime

from mongoengine import *
from mongoengine.signals import pre_save, post_save

from tentd.documents import db, EntityMixin, KeyPair
from tentd.lib.mongoengine import URIField
from tentd.utils import json_attributes, time_to_string

class Relationship(EntityMixin, db.Document):
    """A tent entity related to a local pytentd Entity"""

    meta = {
        'abstract': True,
        'allow_inheritance': False,
        'indexes': ['identity'],
    }

    #: The identity of the related entity
    identity = URIField(required=True, unique_with='entity')

    #: The time the follower was created
    created_at = DateTimeField(required=True, default=datetime.now)

    #: The time the follower was last updated
    updated_at = DateTimeField(required=True, default=datetime.now)

    #: The groups the related entity is a member of
    groups = NotImplemented

    #: The permissions assigned to the related entity
    permissions = NotImplemented

    def to_json(self, more=None):
        json = {
            'id': str(self.id),
            'entity': self.identity,
            'created_at': time_to_string(self.created_at),
            'updated_at': time_to_string(self.updated_at),
            'groups': self.groups,
            'permissions': self.permissions,
        }
        if more is not None:
            json.update(more)
        return json

    @staticmethod
    def pre_save(sender, document, **kwargs):
        document.updated_at = datetime.now()

class Follower(Relationship):
    """An entity following an Entity"""

    #: The Server/API root of the follower
    servers = ListField(URIField(), required=True)

    #: The follower's notification path
    notification_path = StringField(required=True)
    
    licenses = NotImplemented
    types = NotImplemented

    @property
    def keypair(self):
        return KeyPair.objects.get(owner=self)

    def __repr__(self):
        return "<Follower: {}>".format(self.identity)

    def to_json(self):
        return super(Follower, self).to_json({
            'servers': self.servers,
            'notification_path': self.notification_path,
            'licenses': self.licenses,
            'types': self.types,
        })

class Following(Relationship):
    """An entity being followed by an Entity"""

    pass

post_save.connect(KeyPair.owner_post_save, sender=Follower)
pre_save.connect(Relationship.pre_save, sender=Follower)
