"""Additions to mongoengine"""

from __future__ import absolute_import

from rfc3987 import get_compiled_pattern
from mongoengine import URLField

__all__ = ['URIField']

class URIField(URLField):
    """An inproved version of mongoengine.URLField"""

    _URL_REGEX = get_compiled_pattern('^%(URI)s$')
