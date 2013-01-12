"""
Data model for tent auth
"""

from tentd.models import db

class KeyPair(db.Model):
    """KeyPair objects are used to store mac id/key pairs for signing requests"""

    mac_id =  Column(String(32), unique=True)
    mac_key = Column(String(64))
