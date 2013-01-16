"""
Data model for tent auth
"""

from tentd.models import db

class KeyPair(db.Model):
    """KeyPair objects are used to store mac id/key pairs for signing requests"""

    mac_id =  Column(String(32), unique=True)
    mac_key = Column(String(64))
    mac_algorithm = Column(String(24))

    def __init__(self, **kwargs):
        super(KeyPair, self).__init__(**kwargs)
