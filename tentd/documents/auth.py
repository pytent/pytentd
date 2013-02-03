"""
Data model for tent auth
"""

from mongoengine import *

from tentd.documents import db

class KeyPair(db.Document):
    """KeyPair objects are used to store mac id/key pairs for signing requests"""

    mac_id = StringField(max_length=32,unique=True)  
    mac_key = StringField(max_length=64)
    mac_algorithm = StringField(max_length=15)

    def __init__(self, **kwargs):
        super(KeyPair, self).__init__(**kwargs)
