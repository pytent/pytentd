"""Tentd post types"""

from datetime import datetime
from time import mktime

from mongoengine import (DateTimeField, DictField, IntField, StringField, URLField)

from tentd.models import db
from tentd.models.entity import Entity

EntityRefrence = lambda: ReferenceField(
    'Entity', required=True, reverse_delete_rule='CASCADE')

def time_to_string(time_field):
    return mktime(time_field.timetuple())

def maybe(object, dictonary, attribute_name, func=None):
    """Adds a named attribute from object to a dictionary, only if the object
    has such an attribute.

    If no such attribute exists, the function does nothing.

    :Parameters:
    - object: The object to fetch the attribute from
    - dictionary (dict): The dictionary to add to
    - attribute_name (str): The name of the attribute to fetch
    - func (function): A function that can modify the return value
    """
    if hasattr(object, attribute_name):
        value = getattr(object, attribute_name)
        if func is not None:
            value = func(value)
        dictonary[attribute_name] = value

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

    # TODO: Can we have backrefs?
    entity = EntityRefrence()
    
    #: The time the post was published
    published_at = DateTimeField()
    
    #: The time we received the post from the publishing server
    received_at = DateTimeField()

    schema = StringField(required=True)

    content = DictField()
    
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
            'id': self._id,
            'type': self.schema,
            'content': self.content,
        }
        maybe(self, json, 'entity', lambda value: value.core.identity)
        maybe(self, json, 'published_at', time_to_string)
        maybe(self, json, 'received_at', time_to_string)
        return json
