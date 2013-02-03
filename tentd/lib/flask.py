"""Classes and functions that extend or replace parts of Flask"""

from __future__ import absolute_import

import flask

from flask import abort, g, url_for, json, current_app, request
from bson import ObjectId
from mongoengine.queryset import QuerySet
from werkzeug.utils import cached_property
from werkzeug.exceptions import NotFound

from tentd.documents import Entity
from tentd.utils.exceptions import APIBadRequest

class Request(flask.Request):
    """A Request class providing a JSON property"""
    @cached_property
    def json(self):
        if not self.data:
            raise APIBadRequest("No POST data was sent to load json from.")
        try:
            return json.loads(self.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(
                "Could not load json from the POST data ({})".format(e))

class Blueprint(flask.Blueprint):
    """Extends the base Flask Blueprint"""

    @staticmethod
    def _get_endpoint_name(cls):
        """Get a sensible endpoint name from a MethodView class"""
        name = cls.__name__.lower()
        if name.endswith('view'):
            name = name[:-4]
        return name

    def route_class(self, rule='', endpoint=None, **kwargs):
        """Adds a class based view to a blueprint

        The endpoint name is fetched from:
        - The endpoint argument given to route_class()
        - The endpoint attribute of the class
        - The lowercased name of the class
        """
        def decorator(cls):
            name = endpoint or getattr(cls, 'endpoint', None)
            if name is None:
                name = self._get_endpoint_name(cls)
            self.add_url_rule(rule, view_func=cls.as_view(name), **kwargs)
            return cls
        return decorator

class EntityBlueprint(Blueprint):
    """A blueprint that provides g.entity, either using SINGLE_USER_MODE or
    an url prefix of ``/<entity>``

    This class is deprecated
    """
    pass


class JSONEncoder(json.JSONEncoder):
    """Extends the default encoder to be aware of (some) iterables and methods
    that return a json representation of an object"""

    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        
        if hasattr(obj, '__json__'):
            return obj.__json__()
        
        if isinstance(obj, (list, QuerySet)):
            return [self.default(o) for o in obj]

        if isinstance(obj, ObjectId):
            return str(obj)
        
        return super(JSONEncoder, self).default(obj)

def jsonify(obj):
    """Similar to Flask's jsonify() function, but uses a single argument
    and doesn't coerce the arguments into a dictionary"""
    # TODO: Use current_app.json_encoder once Flask 0.10 is availible
    data = json.dumps(obj, cls=JSONEncoder, indent=2)
    return current_app.response_class(data, mimetype='application/json')
