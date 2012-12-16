"""
Data model for tent entities
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey

from tentd.models import db
from tentd.models.profiles import Profile, CoreProfile, BasicProfile

class Entity(db.Model):
    """A tent entity"""
    
    #: The local identifier and primary key
    id = Column(Integer, primary_key=True)
    
    #: The url identifier
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
