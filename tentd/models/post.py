"""Tentd post types"""

__all__ = ['Post']

from mongoengine import *

from tentd.models import db
from tentd.models.entity import EntityMixin
from tentd.utils import time_to_string, maybe

class Post(EntityMixin, db.Document):
    """A post belonging to an entity.
    
    Posts are at the core of Tent. Posts are sent to followers immediately
    after being created.

    This is documented at: https://tent.io/docs/post-types
    """

    #: The post type
    schema = URLField(required=True)

    #: The content of the post
    content = DictField(required=True)
    
    #: The time the post was published
    published_at = DateTimeField()
    
    #: The time we received the post from the publishing server
    received_at = DateTimeField()
    
    def to_json(self):
        """Returns the post as a python dictonary
    
        TODO: 'mentions'
        TODO: 'licenses'
        TODO: 'attachments'
        TODO: 'app'
        TODO: 'views'
        TODO: 'permissions'
        """
        json = {
            'id': self.id,
            'entity': self.entity.core.identity,
            'type': self.schema,
            'content': self.content,
        }
        maybe(json, 'published_at', self.published_at, time_to_string)
        maybe(json, 'received_at', self.received_at, time_to_string)
        return json
