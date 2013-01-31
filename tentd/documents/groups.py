"""Tent groups"""

__all__ = ['Group']

from datetime import datetime

from mongoengine import *

from tentd import __tent_version__ as tent_version
from tentd.documents import db, EntityMixin
from tentd.utils import json_attributes, time_to_string

class Group(EntityMixin, db.Document):
    """Defines a group of entities belonging to a specific entity."""

    meta = {
        'allow_inheritance': False,
        'indexes': ['name'],
    }

    name = StringField(unique_with='entity')
    created_at = DateTimeField(default=datetime.now)
   
    def __init__(self, **kargs):
        super(Group, self).__init__(**kargs)
        if not self.created_at:
            self.created_at = datetime.now

    def __repr__(self):
        return "<Group '{}' [{}]>".format(self.name, self.id)

    def __str__(self):
        return self.name

    def to_json(self):
        return json_attributes(self, 'name', ('created_at', time_to_string))
