"""
Set of functions for enforcing hmac authentication

A set of utilities that implement HMAC authorization as described in the IETF
specification and as required by the tent protocol.

"""

__all__ = ['check_request', 'parse_authstring', 'normalize_request']

import base64
import hmac
from hashlib import sha256, md5
from functools import wraps
from random import getrandbits

from flask import request, Response
from werkzeug.exceptions import Unauthorized

from tentd.documents.auth import KeyPair


def parse_authstring(authstring):
    """Parse an auth string into a dict

    Given an authentication header string [RFC2617], parse the fields and
    return a dict object of each key/pair
    """

    # Ensure the string starts with 'MAC '
    if not authstring or not authstring.startswith('MAC '):
        # TODO: Should this raise an error?
        return False

    pairs = authstring[4:].strip().split(',')

    avars = {}
    for pair in pairs:
        key, value = pair.strip().split("=", 1)
        avars[key] = value.strip('"')

    return avars


def normalize_request(request):
    """Build a normalized request string from a request

    Take the flask request object and build a normalized request string
    as defined in the IETF MAC proposal document

    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01
    """

    auth = parse_authstring(request.headers.get('Authorization'))
    full_path = request.path + "?" + request.query_string
    ext = auth['ext'] if 'ext' in auth else ""

    return "\n".join([
        str(auth['ts']), auth['nonce'], request.method,
        full_path, request.host, str(80), ext])


def check_request(request, key):
    """Return true if the given request object matches its signature

    This is the main test method that verifies that request
    """

    auth = parse_authstring(request.headers.get('Authorization'))

    reqmac = auth['mac']
    norm = normalize_request(request)

    mac = hmac.new(key, norm, sha256)

    macstr = base64.encodestring(mac.digest())
    return reqmac == macstr


def authenticate_response():
    """Sends a 401 response that enables basic auth"""

    return Response('Invalid MAC Credentials\n',
                    401,
                    {'WWW-Authenticate': 'MAC'})


class InvalidAuthentication(Unauthorized):
    def get_description(self, environ):
        return "Invalid MAC credentials"

    def get_headers(self, environ):
        return [('Content-Type', 'text/html'), ('WWW-Authenticate', 'MAC')]


def require_authorization(route):
    """Annotation that forces the view to do HMAC auth


    Apply this decorator to your view to ensure that the browser is
    authenticated. If they are not, they'll get a HTTP 401 and a
    WWW-Authenticate header.

    """
    @wraps(route)
    def require_authorization_for_route(*args, **kwargs):
            """Wrapped decorator function

            TODO: actual implementation of this decorator.
            """

            auth = parse_authstring(request.headers.get('Authorization'))

            if not auth:
                raise InvalidAuthentication

            #try and find a keypair for the given mac id
            try:
                keypair = KeyPair.objects.filter(mac_id=auth['id'])
            except KeyPair.DoesNotExist:
                raise InvalidAuthentication
            return route(*args, **kwargs)
    return require_authorization_for_route
