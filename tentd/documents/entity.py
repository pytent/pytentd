"""Entity, follower and following documents"""

__all__ = ['Entity']

from mongoengine import *
from mongoengine.queryset import DoesNotExist

from tentd.documents import *
from tentd.utils import json_attributes


class QuerySetProperty(object):
    """A set of documents belonging to an entity from another collection

    Basically, provides the functionality a backref would provide."""
    def __init__(self, cls):
        self.cls = cls

    def __get__(self, instance, owner):
        return self.cls.objects(entity=instance)


class Entity(db.Document):
    """A tent entity"""

    meta = {
        'allow_inheritance': False,
        'indexes': ['name'],
    }

    #: The name used as the entities api root
    name = StringField(max_length=100, required=True, unique=True)

    # Querysets belonging to the Entity
    profiles = QuerySetProperty(Profile)
    posts = QuerySetProperty(Post)
    followers = QuerySetProperty(Follower)
    followings = QuerySetProperty(Following)
    notifications = QuerySetProperty(Notification)
    groups = QuerySetProperty(Group)

    @property
    def core(self):
        """Fetch the core profile for the entity"""
        try:
            return Profile.objects.get(schema=CoreProfile.__schema__)
        except DoesNotExist:
            raise Exception("Entity has no core profile.")

    def create_core(self, **kwargs):
        """Creates a coreprofile instance attached to this entity"""
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
                               'followings',
                               'notifications')
