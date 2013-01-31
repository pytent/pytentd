"""Tent groups"""

all = []

from datetime import datetime

from mongoengine import *

from tentd import __tent_version__ as tent_version
from tentd.documents import db, EntityMixin
from tentd.utils import json_attributes

class Group(EntityMixin, db.Document):
    """Defines a group of entities belonging to a specific entity."""

    meta = {
        'allow_inheritance': False,
        'indexes': ['group_name'],
    }

    group_name = StringField(max_length=100, required=True)
    created_at = DateTimeField(default=datetime.now)
   
    def __init__(self, **kargs):
        super(Group, self).__init__(**kargs)
        if not self.created_at:
            self.created_at = datetime.now
 
    def to_json(self):
        return json_attributes(self, 'group_name', 'created_at')
