"""`Followings <https://tent.io/docs/app-server#post-followings>`_"""

__all__ = ['Following']

from datetime import datetime

from mongoengine import DateTimeField

from tentd.documents import db, EntityMixin
from tentd.lib.mongoengine import URIField
from tentd.utils import time_to_string

class Following(EntityMixin, db.Document):
    """An entity that a local entity is following"""

    meta = {
        'allow_inheritance': False,
        'indexes': ['identity'],
    }

    #: The identity of the following
    identity = URIField(unique_with='entity')

    #: The time the following was created
    created_at = DateTimeField(default=datetime.now)
