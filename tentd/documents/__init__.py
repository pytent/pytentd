"""The database models"""

from flask.ext.mongoengine import MongoEngine
from mongoengine import ReferenceField, CASCADE

db = MongoEngine()

class EntityMixin(object):
    """A document mixin which attaches each document to an entity"""

    #: The entity that owns the document
    entity = ReferenceField('Entity', required=True, dbref=False)

# Ensure all models are loaded and imported into the current namespace

from tentd.documents.post import Post
from tentd.documents.profiles import *

from tentd.documents.entity import Entity, Follower, Following
