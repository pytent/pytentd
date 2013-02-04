"""Document classes for authenticaton"""

__all__ = ['KeyPair']

from hashlib import sha256, md5
from random import getrandbits

from mongoengine import StringField, GenericReferenceField

from tentd.documents import db

def generate_id():
    return md5(str(getrandbits(256))).hexdigest()

def generate_key():
    return sha256(str(getrandbits(512))).hexdigest()
    
class KeyPair(db.Document):
    """Stores a mac id/key pair for signing requests"""

    mac_id = StringField(
        max_length=32, unique=True, required=True, default=generate_id)

    mac_key = StringField(
        max_length=64, required=True, default=generate_key)
    
    mac_algorithm = StringField(
        max_length=15, required=True, default="hmac-sha-256")

    def __str__(self):
        return '<KeyPair: {}:{}>'.format(
            self.mac_id, self.mac_algorithm)
