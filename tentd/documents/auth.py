"""Document classes for authenticaton"""

from mongoengine import StringField, GenericReferenceField

from tentd.documents import db
from tentd.documents.followers import Follower

class KeyPair(db.Document):
    """Stores a mac id/key pair for signing requests"""

    owner = GenericReferenceField(choices=(Follower,), required=True)
    mac_id = StringField(max_length=32, unique=True)  
    mac_key = StringField(max_length=64)
    mac_algorithm = StringField(max_length=15)
