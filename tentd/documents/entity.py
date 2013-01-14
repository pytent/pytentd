"""Entity, follower and following documents"""

__all__ = ['Entity', 'Follower', 'Following']

from datetime import datetime

from mongoengine import *
from mongoengine.queryset import DoesNotExist

from tentd.documents import db
from tentd.utils import json_attributes, iterable_to_json, time_to_string

class QuerySetProperty(object):
    """A set of documents belonging to an entity from another collection

    Basically, provides the functionality a backref would provide."""
    def __init__(self, cls):
        self.cls = cls

    def __get__(self, instance, owner):
        return self.cls.objects(entity=instance)

def filter_by_entity(entity, collection):
    """Filters a collection for document owned by the entity"""
    return collection.objects.filter(entity=entity)

class Entity(db.Document):
    """A tent entity"""

    meta = {'allow_inheritance': False}

    #: The name used as the entities api root
    name = StringField(max_length=100, required=True, unique=True)

    # Querysets belonging to the Entity
    # These are all hidden behind lambda functions, as the Documents are not
    # availible at the time this class is defined.
    profiles   = property(lambda self: filter_by_entity(self, Profile))
    posts      = property(lambda self: filter_by_entity(self, Post))
    followers  = property(lambda self: filter_by_entity(self, Follower))
    followings = property(lambda self: [])
    
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
            ('profiles', iterable_to_json),
            ('followers', iterable_to_json),
            ('followings', iterable_to_json))

class EntityMixin(object):
    """A document mixin which attaches each document to an entity"""

    #: The entity that owns the document
    entity = ReferenceField('Entity',
        reverse_delete_rule=CASCADE,
        required=True,
        dbref=False)

class Follower(EntityMixin, db.Document):
    """Someone following an Entity"""

    #: The identity of the follower
    identity = URLField(unique_with='entity')

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
           ('id', str),
            'identity',
           ('created_at', time_to_string),
            'notification_path',
            'permissions',
            'types',
            'licenses')

class Following(db.Document):
    pass

from tentd.documents.post import Post
from tentd.documents.profiles import Profile, CoreProfile
