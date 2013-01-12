"""
Data model for tent entities
"""
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey

from tentd.models import db
from tentd.models.profiles import Profile, CoreProfile, BasicProfile
from tentd.utils import json_attributes

class Entity(db.Model):
    """A tent entity"""
    
    id = Column(Integer, primary_key=True)
    
    #: The name used as the entities api root
    name = Column(String(20), unique=True)

    profiles = db.relationship('Profile', lazy='dynamic')

    @property
    def core(self):
        return self.profiles.filter_by(schema=CoreProfile.__schema__).one()

    def __init__(self, core={}, **kwargs):
        """Creates an Entity and a CoreProfile"""
        super(Entity, self).__init__(**kwargs)
        if not core is None:
            db.session.add(CoreProfile(entity=self, **core))
    
    def __repr__(self):
        return "<{} '{}' [{}]>".format(self.__class__.__name__, self.name, self.id)
    
    def __str__(self):
        """Returns the entities 'name'
        
        Warning: Entity are often used as an argument to url_for,
        so you should avoid changing this.
        """
        return self.name

class Follower(db.Model):
    """Someone following an Entity"""

    id = Column(Integer, primary_key=True)

    # TODO: Make this unique on the owner entity
    identity = Column(String, unique=True)

    #: The time the follower was created
    created_at = Column(DateTime)

    permissions = None
    licenses = None
    types = None

    notification_path = Column(String)

    def __init__(self, **kwargs):
        super(Follower, self).__init__(**kwargs)
        if not self.created_at:
            self.created_at = datetime.utcnow()

    def to_json(self):
        return json_attributes(self,
            'id',
            'identity',
#            'created_at',
            'notification_path',
            'permissions',
            'types',
            'licenses'
        )
