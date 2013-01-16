"""Exception classes"""

from flask import json
from flask.exceptions import JSONHTTPException, BadRequest

class APIException(JSONHTTPException):
    """Our base class for errors that should be returned as JSON"""
    
    def get_body(self, environ):
        """Overrides Flask's JSONHTTPException to use 'error' as the key"""
        return json.dumps({'error': self.get_description(environ)})

class APIBadRequest(APIException, BadRequest):
    """Represents an HTTP ``400 Bad Request`` error, using a JSON response"""
    description = "Malformed request."
