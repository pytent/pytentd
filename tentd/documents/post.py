"""Tentd post types"""

__all__ = ['Post']

from datetime import datetime

from mongoengine import *

from tentd.documents import db, EntityMixin, BetterURLField
from tentd.utils import time_to_string, json_attributes

class Version(db.EmbeddedDocument):
    """A specific version of a Post

    TODO: 'mentions'
    TODO: 'licenses'
    TODO: 'attachments'
    TODO: 'app'
    TODO: 'views'
    TODO: 'permissions'
    """
    meta = {
        'allow_inheritance': False,
    }

    #: The time the post was published
    published_at = DateTimeField(default=datetime.now, required=True)

    #: The time we received the post from the publishing server
    received_at = DateTimeField(default=datetime.now, required=True)

    #: The content of the post
    content = DictField(required=True)

    #: The mentions of this post
    mentions = ListField(BetterURLField)

    def __repr__(self):
        return '<Version {}: {}'.format(self.version, self.content)
    
    def to_json(self):
        return {
            'content': self.content,
            'published_at': time_to_string(self.published_at),
            'received_at':  time_to_string(self.received_at),
            'mentions': self.mentions,
        }

class Post(EntityMixin, db.Document):
    """A post belonging to an entity.
    
    Posts are at the core of Tent. Posts are sent to followers immediately
    after being created.

    This is documented at: https://tent.io/docs/post-types
    """

    meta = {
        'allow_inheritance': False,
        'indexes': ['schema'],
        'ordering': ['-received_at'],
    }

    #: The post type
    schema = BetterURLField(required=True)

    #: The versions of the post
    versions = SortedListField(
        EmbeddedDocumentField(Version),
        ordering='published_at', reverse=True, required=True)

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    @classmethod
    def new(cls, **k):
        """Constucts a Post and an initial version from the same args"""
        # Pop those arguments that are a Version field from the kwargs
        version = {a: k.pop(a) for a in k.keys() if a in Version._fields}
        # Create a new Post with the remaining arguments
        post = cls(**k)
        # And a new Version from the arguments we popped
        post.new_version(**version)
        return post

    def new_version(self, **kwargs):
        """Add a new version of the post"""
        version = Version(**kwargs)
        self.versions.append(version)
        return version

    @property
    def latest(self):
        return self.versions[0]
    
    def to_json(self):
        """Returns the post as a python dictonary"""
        json = {
            'id': self.id,
            'type': self.schema,
            'entity': self.entity.core.identity,
            'version': len(self.versions),
        }
        json.update(self.latest.to_json())
        return json
