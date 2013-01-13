"""The database models"""

from flask.ext.mongoengine import MongoEngine

db = MongoEngine()

# Ensure all models are loaded
from tentd.models.entity import (
    Entity, EntityMixin, Follower, Following)
from tentd.models.profiles import *
from tentd.models.posts import Post
