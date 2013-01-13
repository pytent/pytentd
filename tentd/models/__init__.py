"""The database models"""

from flask.ext.mongoengine import MongoEngine

db = MongoEngine()

# Ensure all models are loaded
from tentd.models.entity import *
from tentd.models.posts import *

