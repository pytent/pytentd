"""The database models"""

from flask.ext.mongoengine import MongoEngine
from mongoengine import CASCADE, ReferenceField

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
