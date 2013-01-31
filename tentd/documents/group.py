"""Tent groups"""

all = []

from mongoengine import *

from tentd import __tent_version__ as tent_version
from tentd.documents import db, BetterURLField, EntityMixin
from tentd.utils import json_attributes

class Group(EntityMixin, db.Document)
    """Defines a group of entities belonging to a specific entity."""
    name = StringField(max_length=255, required=True, unique=True)
    
    def to_json(self):
        return json_attributes(self, 'name')
