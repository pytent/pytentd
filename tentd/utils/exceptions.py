"""Exception classes"""

from flask import json
from flask.exceptions import JSONHTTPException, BadRequest

class APIException(JSONHTTPException):
    """A base class for HTTP errors raised by the API, which should be
    returned with an error message in JSON format"""

    def get_body(self, environ):
        """Returns a JSON description of the exception"""
        return json.dumps(self.get_json(environ))

    def get_json(self, environ):
        return {
            'error': self.get_description(environ),
            'error_class': self.__class__.__name__
        }

class APIBadRequest(APIException, BadRequest):
    """Represents an HTTP ``400 Bad Request`` error"""
    description = "A request was sent that this server could not understand"

class RequestDidNotValidate(APIBadRequest):
    description = "The data in the request could not be validated"
    
    def __init__(self, description=None, validation_errors=None):
        super(RequestDidNotValidate, self).__init__(description)
        self.validation_errors = validation_errors

    def get_json(self, environ):
        json = super(RequestDidNotValidate, self).get_json(environ)
        json['validation_errors'] = self.validation_errors
        return json
