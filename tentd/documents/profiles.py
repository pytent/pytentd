"""Profile info types - https://tent.io/docs/info-types"""

__all__ = ['Profile', 'CoreProfile', 'GenericProfile']

from flask import current_app, url_for
from mongoengine import *

from tentd import __tent_version__ as tent_version
from tentd.documents import db, EntityMixin
from tentd.utils import json_attributes
from tentd.lib.mongoengine import URIField


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
    schema = URIField(unique_with='entity', required=True)
    permissions = DictField()

    def __new__(cls, *args, **kwargs):
        """If ``schema`` is included in the argument list, return a profile
        object using the correct class."""
        if 'schema' in kwargs:
            cls = GenericProfile
            if CoreProfile.__schema__ == kwargs['schema']:
                cls = CoreProfile
        return super(Profile, cls).__new__(cls, *args, **kwargs)

    def __init__(self, **kwargs):
        if self.__class__ is Profile:
            raise NotImplementedError("This class is abstract.")

        super(Profile, self).__init__(**kwargs)

        # Use the classes default schema if it is availible and no schema has
        # been given. TODO: test this
        if not self.schema and hasattr(self.__class__, '__schema__'):
            self.schema = self.__class__.__schema__

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.schema)

    def update_values(self, values):
        raise NotImplementedError("This class is abstract.")


class CoreProfile(Profile):
    """This model provides the Core profile info type.

    Documentation on this profile type can be found here:
    https://tent.io/docs/info-types#core

    TODO: Add licence and server relationships
    """

    meta = {
        'indexes': [{
            'fields': ['identity'],
            'sparse': True,
        }],
    }

    __schema__ = 'https://tent.io/types/info/core/v0.1.0'

    #: The canonical entity identity
    identity = URIField(unique_with='entity', required=True)

    servers = ListField(URIField())

    def __init__(self, *args, **kwargs):
        """Sets public permissions and a default identity"""
        super(CoreProfile, self).__init__(*args, **kwargs)
        self.permissions['public'] = True
        if not self.identity and self.entity is not None:
            self.identity = url_for(
                'entity.profiles', entity=self.entity, _external=True)

    def to_json(self):
        return {
            'entity': self.identity,
            'licences': [],
            'servers': self.servers,
            'tent_version': tent_version
        }

    def update_values(self, values):
        if 'identity' in values:
            self.identity = values['identity']
        if 'servers' in values:
            self.servers = values['servers']


class GenericProfile(db.DynamicDocument, Profile):
    def to_json(self):
        # TODO: test this
        return json_attributes(self, *self._dynamic_fields)

    def update_values(self, values):
        #TODO write this
        pass
