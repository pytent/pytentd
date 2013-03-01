"""HTTP methods"""

__all__ = [
    'HTTP', 'DELETE', 'GET', 'HEAD', 'PUT', 'POST',
    'SDELETE', 'SGET', 'SHEAD', 'SPUT', 'SPOST']

from re import match

from flask import current_app, json, url_for, g
from werkzeug.datastructures import Headers

from tentd.lib.flask import JSONEncoder

def authorization_header():
    """Generates an Authorization header for secure requests"""
    macid  = "s:f5949a1d"
    tstamp = 1355181298
    nonce  = "b07235"
    mac    = "swgy4RpdIBaFpA1hmAbZrph24VVg9FwmJgMm9GkgiLE="

    return 'MAC id="{0}",ts="{1}",nonce="{2}",mac="{3}"'.format(
        macid, tstamp, nonce, mac)

def build_url(endpoint, base_url=None, **kwargs):
    if endpoint[0] == '/':
        return endpoint, base_url

    try:
        url = url_for(endpoint, **kwargs)
    except KeyError:
        raise Exception("Endpoint does not exist")

    result = match("(http://[^/]+)(/.*)", url)
    if result:
        base_url, url = result.groups()

    return url, base_url

def HTTP(type, endpoint, data=None, secure=False,
    headers=None, content_type='text/html', **kwargs):
    """A HTTP convenience function that takes a method type, an endpoint
    name, and optionally data or JSON to send.

    The endpoint argument is used to build an url using url_for, along
    with **kwargs. If it starts with a /, it is used as-is. If the data
    argument is a dict or list, it will be dumped to JSONEncoder

    Internally, it calls current_app.client.<method> to get the response.
    """
    
    url, base_url = build_url(endpoint, **kwargs)
    
    if isinstance(data, (dict, list)):
        data = json.dumps(data, cls=JSONEncoder)
        content_type = 'application/json'

    if not hasattr(current_app, 'client'):
        raise NotImplementedError(
            "The application requires a test client")

    # Ensure ``headers`` is of type Headers
    if not isinstance(headers, Headers):
        headers = Headers(headers or {})

    # Emulate a HMAC request if needed
    if secure:
        headers.set('Authorization', authorization_header())

    # Fetch and call the function from the client
    return getattr(current_app.client, type)(
        url, base_url=base_url,
        data=data, headers=headers, content_type=content_type)

def _wrap_http(method_name):
    return lambda *a, **k: HTTP(method_name, *a, **k)

def _wrap_http_secure(method_name):
    return lambda *a, **k: HTTP(method_name, *a, secure=True, **k)

DELETE  = _wrap_http('delete')
GET     = _wrap_http('get')
HEAD    = _wrap_http('head')
POST    = _wrap_http('post')
PUT     = _wrap_http('put')

SDELETE = _wrap_http_secure('delete')
SGET    = _wrap_http_secure('get')
SHEAD   = _wrap_http_secure('head')
SPOST   = _wrap_http_secure('post')
SPUT    = _wrap_http_secure('put')
