"""Data model for tent entities"""

from datetime import datetime

from mongoengine import *
from mongoengine.queryset import DoesNotExist

from tentd import __tent_version__ as tent_version
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
            return BaseProfile.objects.get(schema=CoreProfile.__schema__)
        except DoesNotExist:
            raise Exception("Entity has no core profile.")
    
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
    #: The entity that owns this document
    entity = ReferenceField('Entity', required=True, reverse_delete_rule=CASCADE, dbref=False)

class BaseProfile(EntityMixin, db.Document):
    """A profile information type belonging to an entity

    The Profile class is an abstract type, defining the relationship between
    an entity and it's profiles, and holding the schema url for the type.

    An entity cannot have multiple profiles with the same schema.

    See: https://tent.io/docs/info-types
    """
    meta = {
        'collection': 'profile',
        'allow_inheritance': True,
        'indexes': ['schema'],
    }

    #: The info type schema
    schema = URLField(unique_with='entity', required=True)

    def __init__(self, **kwargs):
        if self.__class__ is Profile:
            raise NotImplementedError("This class is abstract.")

        super(BaseProfile, self).__init__(**kwargs)

        # Use the classes default schema if it is availible and no schema has
        # been given. TODO: test this
        if not self.schema and hasattr(self.__class__, '__schema__'):
            self.schema = self.__class__.__schema__

class CoreProfile(BaseProfile):
    """This model provides the Core profile info type.

    Documentation on this profile type can be found here:
    https://tent.io/docs/info-types#core

    TODO: Add licence and server relationships
    """

    meta = {
        'indexes': [{
            'fields': ['identity'],
            'unique': True,
            'sparse': True,
        }],
    }
    
    __schema__ = 'https://tent.io/types/info/core/v0.1.0'

    #: The canonical entity identity
    # The generated url for the entity can be found at
    # url_for('base.link', entity=self.entity, _external=True)
    identity = URLField(required=True)

    servers = ListField(URLField())

    def to_json(self):
        return {
            'entity': self.identity,
            'licences': [],
            'servers': [],
            'tent_version': tent_version
        }

class BasicProfile(BaseProfile):
    """The Basic profile info type.

    The Basic profile helps humanize users. All fields are optional but help
    provide a context in which to place a user's details.

    See: https://tent.io/docs/info-types#basic
    """

    __schema__ = 'https://tent.io/types/info/basic/v0.1.0'

    avatar_url = URLField()

    name       = StringField()
    location   = StringField()
    gender     = StringField()

    birthdate  = StringField() # TODO: ?
    bio        = StringField()

    def to_json(self):
        return json_attributes(self,
            'avatar_url',
            'name',
            'location',
            'gender',
            'birthdate',
            'bio'
        )

class Profile(BaseProfile, db.DynamicDocument):
    def to_json(self):
        # TODO: test this
        return json_attributes(self, *self._dynamic_fields)

# TODO: Move followers to their own module
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
