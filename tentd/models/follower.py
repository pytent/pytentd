
from sqlalchemy import Column, String, Integer

import time

from tentd.models import db

class Follower(db.Model):
    id = Column(String, primary_key = True)
    entity = Column(String)
    created_at = Column(Integer)
    permissions = None
    licenses = None
    types = None
    notification_path = Column(String)


    def __init__(self, **kwargs):
        self.entity = kwargs['entity']
        self.permissions = kwargs['permissions']
        self.types = kwargs['types']
        self.notification_path = kwargs['notification_path']
        self.created_at = int(time.time())

    def __json__(self):
        return {name: getattr(self, name) for name in [
            'id',
            'entity',
            'created_at',
            'notification_path',
            'permissions',
            'types',
            'licenses'
        ]}
