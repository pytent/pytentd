__all__ = ['URIField']

import rfc3987
from mongoengine.fields import URLField

class URIField(URLField):
    """An inproved version of mongoengine.URLField"""

    _URI_REGEX = rfc3987.get_compiled_pattern('^%(URI)s$')

    def __init__(self, verify_exists=False, url_regex=_URI_REGEX, **kwargs):
        super(URIField, self).__init__(verify_exists=verify_exists, 
            url_regex=url_regex, **kwargs)
