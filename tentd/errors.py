from flask import json
from flask.exceptions import JSONHTTPException, BadRequest

class TentError(Exception):
    def __init__(self, message, status):
        self.reason = message
        self.status = status

class JSONException(JSONHTTPException):
    """Our base class for errors that should be returned as JSON"""
    def get_body(self, environ):
        """Overrides Flask's JSONHTTPException to use 'error' as the key"""
        return json.dumps(dict(error=self.get_description(environ)))

class JSONBadRequest(JSONException, BadRequest):
    """Represents an HTTP ``400 Bad Request`` error, using a JSON response"""
    description = (
        "The browser (or proxy) sent a request"
        "that this server could not understand.")
