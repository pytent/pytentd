"""The database models"""

from flask.ext.mongoengine import MongoEngine
from mongoengine import ReferenceField, CASCADE

db = MongoEngine()

class EntityMixin(object):
    """A document mixin which attaches each document to an entity"""

    #: The entity that owns the document
    entity = ReferenceField('Entity', reverse_delete_rule=CASCADE, required=True, dbref=False)

# Ensure all models are loaded (Loading order should be irrelevant, though
# this is because all of the dependencies are one way)
from tentd.models.entity import *
from tentd.models.posts import *
from tentd.models.profiles import *
