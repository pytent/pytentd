"""Pytentd test suite"""

__all__ = ['GET', 'PUT', 'POST', 'HEAD']

from flask import current_app, json, url_for, g
from py.test import main
from werkzeug.datastructures import ImmutableDict, Headers

from tentd.lib.flask import JSONEncoder

class HTTP(object):
    """HTTP convenience functions that take an endpoint name,
    and optionally data or JSON to send"""

    macid  = "s:f5949a1d"
    tstamp = 1355181298
    nonce  = "b07235"
    mac    = "swgy4RpdIBaFpA1hmAbZrph24VVg9FwmJgMm9GkgiLE="
    
    def __init__(self, function_name):
        """Creates a HTTP function using the name of the method that will be
        called on ``current_app.client``"""
        self.function_name = function_name

    def authentication_header(self):
        return 'MAC id="{0}",ts="{1}",nonce="{2}",mac="{3}"'.format(
            self.macid, self.tstamp, self.nonce, self.mac)

    def __call__(self, endpoint, data=None, secure=False,
        headers=None, content_type='text/html', **kwargs):
        """Call current_app.client.<function> and return the response.

        The endpoint argument is used to build an url using url_for, along
        with **kwargs. If it starts with a /, it is used as-is. If the data
        argument is a dict or list, it will be dumped to JSON"""
        if not endpoint[0] == '/':
            endpoint = url_for(endpoint, **kwargs)
        
        if isinstance(data, (dict, list)):
            data = json.dumps(data, cls=JSONEncoder)
            content_type = 'application/json'

        if not hasattr(current_app, 'client'):
            raise NotImplementedError(
                "The application requires a test client")

        headers = headers or Headers()
        
        # Emulate a HMAC request if needed
        if secure:
            headers.set('Authorization', self.authentication_header())

        # Fetch and call the function from the client
        http_function = getattr(current_app.client, self.function_name)
        return http_function(
            endpoint, data=data, headers=headers, content_type=content_type)

# Generate the HTTP Methods
for method_name in ('delete', 'get', 'head', 'post', 'put'):
    locals()[method_name.upper()] = HTTP(method_name)

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
