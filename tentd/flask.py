"""Classes and functions that extend flask"""

from __future__ import absolute_import

from flask import abort, g, url_for, json
from flask import Blueprint as FlaskBlueprint, Request as FlaskRequest
from werkzeug.utils import cached_property

from tentd.documents import Entity
from tentd.utils.exceptions import APIBadRequest

class Request(FlaskRequest):
    @cached_property
    def json(self):
        if not self.data:
            raise APIBadRequest("No POST data was sent to load json from.")
        try:
            return json.loads(self.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(
                "Could not load json from the POST data ({})".format(e))

class Blueprint(FlaskBlueprint):
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
    """A blueprint prefixed with /<entity>

    It provides link headers and g.entity"""
    
    def __init__(self, *args, **kwargs):
        super(EntityBlueprint, self).__init__(*args, **kwargs)
        self.url_prefix = '/<string:entity>' + kwargs.get('url_prefix', '')
        self.after_request(self.add_profile_link)
        self.url_value_preprocessor(self.fetch_entity)

    @staticmethod
    def add_profile_link(response):
        """Add the link header to the response if the entity is set"""
        if hasattr(g, 'entity'):
            link = url_for('entity.profile', entity=g.entity, _external=True)
            header = '<{}>; rel="https://tent.io/rels/profile"'.format(link)
            response.headers['Link'] = header
        return response

    @staticmethod
    def fetch_entity(endpoint, values):
        """Set g.entity using the entity name given in the url"""
        try:
            g.entity = Entity.objects.get(name=values.pop('entity'))
        except Entity.DoesNotExist:
            abort(404)
