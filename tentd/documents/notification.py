""" pytentd notification """

__all__ = ['Notification']

from mongoengine import *
from datetime import datetime
from tentd.documents import db, EntityMixin
from tentd.utils import time_to_string, json_attributes

class Notification(EntityMixin, db.Document):
    """ A notification belonging to an Entity. """


    received_at = DateTimeField(required=True)
    post_id = StringField(required=True)
