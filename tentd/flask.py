"""Classes and functions that extend flask"""

from __future__ import absolute_import

from flask import abort, g, url_for, json, current_app
from flask import Blueprint as FlaskBlueprint, Request as FlaskRequest
from werkzeug.utils import cached_property
from werkzeug.exceptions import NotFound

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
    """A blueprint that provides g.entity, either using SINGLE_USER_MODE or
    an url prefix of ``/<entity>``"""
    
    def __init__(self, *args, **kwargs):
        """Register the link header and prepossessor functions"""
        super(EntityBlueprint, self).__init__(*args, **kwargs)
        self.after_request(self.add_profile_link)
        self.url_value_preprocessor(self.fetch_entity)

    @staticmethod
    def _single_user_mode():
        """Return the value of the SINGLE_USER_MODE option"""
        return current_app.config.get('SINGLE_USER_MODE', None)

    @classmethod
    def add_profile_link(cls, response):
        """Add the link header to the response if the entity is set"""
        if hasattr(g, 'entity'):
            options = {'_external': True}
            if not cls._single_user_mode():
                options['entity'] = g.entity
            response.headers['Link'] = '<{link}>; rel="{rel}"'.format(
                link=url_for('entity.profile', **options),
                rel='https://tent.io/rels/profile')
        return response

    @classmethod
    def fetch_entity(cls, endpoint, values):
        """Set g.entity using the entity name given in the url, or the name
        given in the app configuration under SINGLE_USER_MODE"""
        try:
            name = cls._single_user_mode() or values.pop('entity')
            g.entity = Entity.objects.get(name=name)
        except Entity.DoesNotExist:
            raise NotFound("User does not exist")

    def prefix(self, app):
        """Get the url prefix for the blueprint, using the app configuration
        and the blueprint-specific url prefix. This is used when registering
        the blueprint."""
        url_prefix = ''
        
        if not app.config.get('SINGLE_USER_MODE', None):
            url_prefix += '/<string:entity>'

        if self.url_prefix is not None:
            url_prefix += self.url_prefix

        return url_prefix if url_prefix else None
