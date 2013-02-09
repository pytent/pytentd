"""Pytentd test suite"""

__all__ = ['GET', 'PUT', 'POST', 'HEAD']

from flask import current_app, json, url_for, g
from py.test import main
from werkzeug.datastructures import ImmutableDict, Headers

from tentd.lib.flask import JSONEncoder

def authorization_header():
    """Generates an Authorization header for secure requests"""
    macid  = "s:f5949a1d"
    tstamp = 1355181298
    nonce  = "b07235"
    mac    = "swgy4RpdIBaFpA1hmAbZrph24VVg9FwmJgMm9GkgiLE="

    return 'MAC id="{0}",ts="{1}",nonce="{2}",mac="{3}"'.format(
        macid, tstamp, nonce, mac)

def HTTP(type, endpoint, data=None, secure=False,
    headers=None, content_type='text/html', **kwargs):
    """A HTTP convenience function that takes a method type, an endpoint
    name, and optionally data or JSON to send.

    The endpoint argument is used to build an url using url_for, along
    with **kwargs. If it starts with a /, it is used as-is. If the data
    argument is a dict or list, it will be dumped to JSONEncoder

    Internally, it calls current_app.client.<method> to get the response.
    """
    if not endpoint[0] == '/':
        endpoint = url_for(endpoint, **kwargs)

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
        endpoint, data=data, headers=headers, content_type=content_type)

def _wrap_http(method_name):
    return lambda *args, **kwargs: HTTP(method_name, *args, **kwargs)

DELETE = _wrap_http('delete')
GET = _wrap_http('get')
HEAD = _wrap_http('head')
POST = _wrap_http('post')
PUT = _wrap_http('put')

def profile_url_for(entity, _external=False):
    """Get an entity profile url without using url_for"""
    url = ['/profile']

    if not current_app.single_user_mode:
        url.append('/' + entity.name)

    if _external:
        url.append('http://' + current_app.config['SERVER_NAME'])

    return ''.join(url[::-1])

def response_has_link_header(response):
    """Test that a response includes an entity link header"""
    link = '<{}>; rel="https://tent.io/rels/profile"'.format(
        profile_url_for(g.entity, _external=True))
    return response.headers['Link'] == link

if __name__ == '__main__':
    main()
