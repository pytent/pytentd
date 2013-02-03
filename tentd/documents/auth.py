"""Document classes for authenticaton"""

from mongoengine import StringField

from tentd.documents import db

class KeyPair(db.Document):
    """Stores a mac id/key pair for signing requests"""

    mac_id = StringField(max_length=32, unique=True)  
    mac_key = StringField(max_length=64)
    mac_algorithm = StringField(max_length=15)
