"""Pytentd test suite"""

__all__ = ['GET', 'PUT', 'POST', 'HEAD']

from flask import current_app, json, url_for
from py.test import main

from tentd.lib.flask import JSONEncoder

class HTTP(object):
    """HTTP convenience functions that take an endpoint name,
    and optionally data or JSON to send"""
    
    def __init__(self, function_name):
        """Creates a HTTP function using the name of the method that will be
        called on ``current_app.client``"""
        self.function_name = function_name

    def __call__(self, endpoint, data=None, **kwargs):
        """Call current_app.client.<function> and return the response

        If the data argument is a dict or list, it will be dumped to JSON"""
        if isinstance(data, (dict, list)):
            data = json.dumps(data, cls=JSONEncoder)

        if not hasattr(current_app, 'client'):
            raise NotImplementedError("App requires a test client")

        http_function = getattr(current_app.client, self.function_name)
        return http_function(url_for(endpoint, **kwargs), data=data)

GET, PUT, POST, HEAD = HTTP('get'), HTTP('put'), HTTP('post'), HTTP('head')

if __name__ == '__main__':
    main()
