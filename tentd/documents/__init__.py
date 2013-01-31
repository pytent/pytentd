"""The database models"""

from flask.ext.mongoengine import MongoEngine
from mongoengine import CASCADE, ReferenceField, StringField, ValidationError
from requests import get
from rfc3987 import parse

class BetterURLField(StringField):
    """An inproved version of mongoengine.URLField"""

    # TODO: Replace all URLFields with this
    # TODO: Use verify_exists where needed

    def __init__(self, verify_exists=False, **kwargs):
        super(BetterURLField, self).__init__(**kwargs)
        self.verify_exists = verify_exists

    def validate(self, value):
        """Check that the URL is valid, and optionally accessible."""
        try:
            parse(value)
        except ValueError:
            print value
            self.error("Value is not a valid URL")

        if self.verify_exists:
            try:
                get(value)
            except:
                self.error("The URL appears to be inaccessible")

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
