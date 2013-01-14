"""Profile info types - https://tent.io/docs/info-types"""

__all__ = ['Profile', 'CoreProfile', 'BasicProfile', 'GenericProfile']

from mongoengine import *

from tentd import __tent_version__ as tent_version
from tentd.documents import db
from tentd.documents.entity import EntityMixin
from tentd.utils import json_attributes

class Profile(EntityMixin, db.Document):
    """A profile information type belonging to an entity

    The Profile class is an abstract type, defining the relationship between
    an entity and it's profiles, and holding the schema url for the type.

    An entity cannot have multiple profiles with the same schema.
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

        super(Profile, self).__init__(**kwargs)

        # Use the classes default schema if it is availible and no schema has
        # been given. TODO: test this
        if not self.schema and hasattr(self.__class__, '__schema__'):
            self.schema = self.__class__.__schema__

class CoreProfile(Profile):
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

class BasicProfile(Profile):
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

class GenericProfile(db.DynamicDocument, Profile):
    def to_json(self):
        # TODO: test this
        return json_attributes(self, *self._dynamic_fields)