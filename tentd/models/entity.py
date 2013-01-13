"""Data model for tent entities"""

from datetime import datetime
from mongoengine import (DateTimeField, DictField, IntField, ListField,
    StringField, ReferenceField, URLField)

from tentd.models import db
from tentd.models.profiles import CoreProfile
from tentd.utils import json_attributes

class Entity(db.Document):
    """A tent entity"""
    
    #: The name used as the entities api root
    name = StringField(max_length=100, primary_key=True, unique=True)

    test = StringField()

    profiles = DictField()

    #: The entities this entity is being followed by
    followers = ListField()

    #: The entities this entity is following
    followings = ListField()

    @property
    def core(self):
        """Fetch the core profile for the entity"""
        return self.profiles.filter_by(schema=CoreProfile.__schema__).one()
    
    def __repr__(self):
        return "<Entity '{}' [{}]>".format(self.name, self.id)
    
    def __str__(self):
        """Returns self.name

        Avoid changing this behaviour, as it allows the entity to be used in
        url_for calls without explicitly stating that the name is being used
        """
        return self.name

    def to_json(self):
        return json_attributes(self,
            'name',
            'profiles',
            'followers',
            'followings')

class Follower(db.Document):
    """Someone following an Entity"""

    #: The entity the follower is following
    owner = ReferenceField(Entity, reverse_delete_rule='CASCADE', dbref=False)

    #: The identity of the follower
    identity = URLField(unique_with='owner')

    #: The time the follower was created
    created_at = DateTimeField()

    permissions = None
    licenses = None
    types = None

    notification_path = StringField()

    def __init__(self, **kwargs):
        super(Follower, self).__init__(**kwargs)
        if not self.created_at:
            self.created_at = datetime.utcnow()

    def to_json(self):
        return json_attributes(self,
            'id',
            'identity',
#           'created_at', # TODO: Modify json_attributes() to take a function?
            'notification_path',
            'permissions',
            'types',
            'licenses')
