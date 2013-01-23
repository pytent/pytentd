"""Exception classes"""

from flask import json
from flask.exceptions import JSONHTTPException, BadRequest

class APIException(JSONHTTPException):
    """A base class for HTTP errors raised by the API, which should be
    returned with an error message in JSON format"""
    
    def get_body(self, environ):
        """Overrides Flask's JSONHTTPException to use 'error' as the key"""
        return json.dumps({'error': self.get_description(environ)})

class APIBadRequest(APIException, BadRequest):
    """Represents an HTTP ``400 Bad Request`` error"""
    description = "A request was sent that this server could not understand"
