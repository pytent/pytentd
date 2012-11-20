'''
Data model and bindings for tent users

'''

from sqlalchemy import Column, Integer, String
from tent.data.dbm import Base, TableMixin

class User(Base,TableMixin):
    '''
    User class contains all profile information about a tent user entity
    '''

    entity_id  = Column(String, primary_key=True)
    licenses   = []
    servers    = []
    name       = Column(String)
    avatar_url = Column(String)
    birthdate  = Column(String)
    location   = Column(String)
    gender     = Column(String)
    bio        = Column(String)


    def __init__(self, name):
        self.name = name
        self.entity_id = "http://localhost/%s" % name.lower().replace(' ','.')
