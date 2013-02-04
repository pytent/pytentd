__all__ = ['URIField']

from rfc3987 import get_compiled_pattern
from mongoengine.fields import URLField

class URIField(URLField):
    """An inproved version of mongoengine.URLField"""

    _URL_REGEX = get_compiled_pattern('^%(URI)s$')
