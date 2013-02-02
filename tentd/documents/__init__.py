"""The database models"""

from flask.ext.mongoengine import MongoEngine
from mongoengine import CASCADE, ReferenceField, ValidationError, URLField
from requests import get
import rfc3987

class BetterURLField(URLField):
    """An inproved version of mongoengine.URLField"""

    # TODO: Replace all URLFields with this
    # TODO: Use verify_exists where needed

    _URI_REGEX = rfc3987.get_compiled_pattern('^%(URI)s$')

    def __init__(self, verify_exists=False, url_regex=_URI_REGEX, **kwargs):
        super(BetterURLField, self).__init__(verify_exists=verify_exists, 
            url_regex=url_regex, **kwargs)

class EntityMixin(object):
    """A document mixin which attaches each document to an entity"""

    #: The entity that owns the document
    entity = ReferenceField('Entity', required=True, dbref=False)

db = MongoEngine()

# Ensure all models are loaded and imported into the current namespace

from tentd.documents.followers import Follower, Following
from tentd.documents.post import Post
from tentd.documents.profiles import *
from tentd.documents.notification import Notification
from tentd.documents.groups import Group

# Entity must be loaded last, as it relies on querysets from other documents
from tentd.documents.entity import Entity

# Create the deletion rules
# CASCADE is used so that documents owned by an entity are deleted with it
for collection in (Follower, Following, Post, Profile):
    Entity.register_delete_rule(collection, 'entity', CASCADE)

# Clean the namespace, as defining __all__ leads to problems
del MongoEngine, ReferenceField, CASCADE
