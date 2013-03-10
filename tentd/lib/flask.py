"""Classes and functions that extend or replace parts of Flask"""

from __future__ import absolute_import

from functools import wraps

from bson import ObjectId
from flask import json, current_app, Request, Response, Blueprint, request
from mongoengine.queryset import QuerySet
from werkzeug.utils import cached_property

from tentd.utils.exceptions import APIBadRequest

__all__ = ['Request', 'Response', 'Blueprint', 'JSONEncoder', 'jsonify']


def cached_method(func):
    """Caches the return value of a function"""
    @wraps(func)
    def cache_return_value(self, *args, **kwargs):
        """Store the function's result in self._cache and return it"""
        name = '_cached_' + func.__name__
        if not hasattr(self, name):
            setattr(self, name, func(self, *args, **kwargs))
        return getattr(self, name)
    return cache_return_value


class JSONMixin(object):
    """Adds a cached JSON method for use with Request and Response

    This provides a standard api for fetching json between the requests
    library and the Request/Response classes"""

    accepted_json_mimetypes = (
        'application/json',
        'application/vnd.tent.v0+json')

    @cached_method
    def json(self):
        try:
            if self.mimetype in self.accepted_json_mimetypes:
                request_charset = self.mimetype_params.get('charset')
                if request_charset is not None:
                    return json.loads(self.data, encoding=request_charset)
                return json.loads(self.data)
            else:
                raise Exception("Response is not JSON")
        except Exception as error:
            return self.on_json_loading_failed(error)

    def on_json_loading_failed(self, error):
        """A stub method that raises the error it is given

        Used for compatibility with Request"""
        raise error


class Request(JSONMixin, Request):
    def on_json_loading_failed(self, e):
        raise APIBadRequest(
            "The request data could not be parsed as JSON ({})".format(e))


class Response(JSONMixin, Response):
    pass


class Blueprint(Blueprint):
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

from flask import current_app, g, url_for
from tentd.documents import Entity
from werkzeug.exceptions import NotFound

class EntityBlueprint(Blueprint):
    """A blueprint that provides g.entity, either using SINGLE_USER_MODE or
    an url prefix of ``/<entity>``
    """

    def __init__(self, *args, **kwargs):
        super(EntityBlueprint, self).__init__(*args, **kwargs)

        self.url_value_preprocessor(self._assign_global_entity)
        self.url_defaults(self._use_global_entity)
        self.url_defaults(self._pop_global_entity)
        self.after_request(self._link_header)

    def _assign_global_entity(self, endpoint, values):
        """Assign the current entity to g.entity"""
        if endpoint:
            try:
                name = current_app.single_user_mode or values.pop('entity')
                g.entity = Entity.objects.get(name=name)
            except Entity.DoesNotExist:
                raise NotFound("The reqested entity was not found")

    def _use_global_entity(self, endpoint, values):
        """Use g.entity as a default value in url_for calls"""
        if current_app.url_map.is_endpoint_expecting(endpoint, 'entity'):
            if hasattr(g, 'entity'):
                values.setdefault('entity', g.entity)

    def _pop_global_entity(self, endpoint, values):
        """Remove entity values in single user mode"""
        if current_app.single_user_mode:
            values.pop('entity', None)

    def _link_header(self, response):
        """Add the entity link header to responses"""
        if hasattr(g, 'entity'):
            link = '<{}>; rel="https://tent.io/rels/profile"'.format(
                url_for('entity.profiles', _external=True))
            response.headers['Link'] = link
        return response

    def register(self, app, options, *args):
        """Register the blueprint with the correct url prefixes"""
        if not app.single_user_mode:
            if app.use_subdomains:
                options['subdomain'] = '<string:entity>'
            else:
                original_prefix = self.url_prefix or ''
                options['url_prefix'] = '/<string:entity>' + original_prefix

        super(EntityBlueprint, self).register(app, options, *args)


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
        if obj is NotImplemented:
            return "Warning: Attribute not implemented"
        return super(JSONEncoder, self).default(obj)


def jsonify(obj):
    """Similar to Flask's jsonify() function, but uses a single argument
    and doesn't coerce the arguments into a dictionary.

    Uses the mimetype of the request if possible, otherwise uses ``application/vnd.tent.v0+json``.

    .. todo: Use current_app.json_encoder once Flask 0.10 is availible
    """
    data = json.dumps(obj, cls=JSONEncoder, indent=2)

    if request.mimetype in ['application/json', 'text/json']:
        mimetype = request.mimetype
    else:
        mimetype = 'application/vnd.tent.v0+json'
    
    return current_app.response_class(data, mimetype=mimetype)
