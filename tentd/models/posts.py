"""Tentd post types"""

from mongoengine import *

from tentd.models import db
from tentd.utils import time_to_string, maybe

class Post(db.Document):
    """A post belonging to an entity.
    
    Posts are at the core of Tent. Posts are sent to followers immediately after
    being created. The tent specifcation defines that there are two ways of
    accessing posts:

    `GET posts/` returns all posts, the parameters of the request define any
    filtering. There may need to be extra filtering for server-side performance.

    `GET posts/<id>` returns a post with the defined id.
    
    This is documented at: https://tent.io/docs/post-types
    """

    entity = ReferenceField('Entity', required=True, reverse_delete_rule=CASCADE, dbref=False)
    
    #: The time the post was published
    published_at = DateTimeField()
    
    #: The time we received the post from the publishing server
    received_at = DateTimeField()

    schema = StringField(required=True)

    content = DictField(required=True)
    
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
