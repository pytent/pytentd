"""Data model for tent entities"""

from datetime import datetime

from mongoengine import *
from mongoengine.queryset import DoesNotExist

from tentd.models import db
from tentd.utils import json_attributes

class Entity(db.Document):
    """A tent entity"""

    meta = {'allow_inheritance': False}
    
    #: The name used as the entities api root
    name = StringField(max_length=100, required=True, unique=True)

    @property
    def posts(self):
        return Post.objects(entity=self)

    @property
    def core(self):
        """Fetch the core profile for the entity"""
        try:
            return Profile.objects.get(schema=CoreProfile.__schema__)
        except DoesNotExist:
            raise Exception("Entity has no core profile.")

    def create_core(self, **kwargs):
        return CoreProfile(entity=self, **kwargs).save()
    
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

class EntityMixin(object):
    """A document mixin which attaches instances of the document to an entity

    Note: Documents using this mixin will be deleted with the entity"""

    #: The entity that owns this document
    entity = ReferenceField('Entity',
        required=True, reverse_delete_rule=CASCADE, dbref=False)

# Profile requires Entity to already be defined
from tentd.models.profiles import Profile, CoreProfile

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
            # 'created_at',
            # TODO: Modify json_attributes() to take a function?
            'notification_path',
            'permissions',
            'types',
            'licenses')

class Following(db.Document):
    pass
