"""The database models"""

from flask.ext.mongoengine import MongoEngine
from mongoengine import CASCADE, ReferenceField, DENY


class EntityMixin(object):
    """A document mixin which attaches each document to an entity"""

    #: The entity that owns the document
    entity = ReferenceField('Entity', required=True, dbref=False)

db = MongoEngine()

# Ensure all models are loaded and imported into the current namespace

from tentd.documents.auth import KeyPair
from tentd.documents.follower import Follower
from tentd.documents.following import Following
from tentd.documents.post import Post
from tentd.documents.profiles import Profile, CoreProfile, GenericProfile
from tentd.documents.notification import Notification
from tentd.documents.groups import Group

# Some document types import others, and should be loaded last
from tentd.documents.entity import Entity

#: A tuple of all documents that provide a mongodb collection
collections = (
    KeyPair, Follower, Following, Post, Profile, Notification, Group, Entity)

# Create the deletion rules
# CASCADE is used so that documents owned by an entity are deleted with it
for collection in (Follower, Following, Post, Profile):
    Entity.register_delete_rule(collection, 'entity', CASCADE)

Follower.register_delete_rule(KeyPair, 'owner', CASCADE)

# Clean the namespace, as defining __all__ leads to problems
del MongoEngine, ReferenceField, CASCADE
