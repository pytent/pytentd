"""SQLAlchemy types"""

from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import MutableType, TypeDecorator, Unicode
from flask import json

class JSONDict(TypeDecorator, MutableType):
    """Represents an immutable structure as a json-encoded string."""

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return unicode(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionaries to MutableDict."""
        if isinstance(value, MutableDict):
            return value
        elif isinstance(value, dict):
            return MutableDict(value)
        # This will raise ValueError
        return Mutable.coerce(key, value)

    def __setitem__(self, key, value):
        """Detect dictionary set events and emit change events."""
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        """Detect dictionary del events and emit change events."""
        dict.__delitem__(self, key)
        self.changed()

MutableDict.associate_with(JSONDict)
