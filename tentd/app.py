"""The create_app function"""

from flask import Flask, current_app, g, url_for
from mongoengine import ValidationError
from werkzeug.exceptions import ImATeapot, NotFound

from tentd import __doc__ as description, __version__ as version
from tentd.lib.flask import Request, Response, JSONEncoder, jsonify
from tentd.blueprints import entity, followers, posts, groups
from tentd.documents import db, Entity
from tentd.utils import make_config
from tentd.utils.exceptions import RequestDidNotValidate

class TentdFlask(Flask):
    """An extension of the Flask class with some custom methods"""

    #: The class used for incoming requests
    request_class = Request

    #: The class used for outgoing responses
    response_class = Response

    #: Not useful until Flask 0.10
    json_encoder = JSONEncoder

    #: Endpoints that we can skip trying to load an entity for
    blank_endpoints = ('home', 'coffee')
    
    def __init__(self, *args, **kwargs):
        """Initialise the application normally and then register several
        necessary functions"""
        super(TentdFlask, self).__init__(*args, **kwargs)

        # Url handlers, mostly used to implement single user mode
        self.url_value_preprocessor(self._url_value_preprocessor)
        self.after_request(self._after_request)
        self.url_defaults(self._url_defaults)

        # Error handlers
        self.errorhandler(ValidationError)(self.validation_error)
    
    @property
    def single_user_mode(self):
        """Returns the value of SINGLE_USER_MODE, defaulting to False"""
        return self.config.get('SINGLE_USER_MODE', None)
    
    def register_entity_blueprint(self, blueprint, **kwargs):
        """Register a blueprint with the /<entity> prefix if needed"""
        url_prefix = '' if self.single_user_mode else '/<string:entity>'
        url_prefix += blueprint.url_prefix or ''
        self.register_blueprint(blueprint, url_prefix=url_prefix, **kwargs)

    def _assign_global_entity(self, name):
        """Set g.entity using an entity name"""
        try:
            g.entity = Entity.objects.get(name=name)
        except Entity.DoesNotExist:
            raise NotFound(
                "Entity '{}' reqested does not exist".format(name))
        
    def _url_value_preprocessor(self, endpoint, values):
        """Work out the entity that is currently in use"""
        if endpoint and endpoint not in self.blank_endpoints:
            # If the endpoint is expecting an entity value,
            # use that to fetch the entity
            if self.url_map.is_endpoint_expecting(endpoint, 'entity'):
                self._assign_global_entity(values.pop('entity'))
            # If we are in single user mode, use that as the name
            # if the endpoint is not marked
            elif self.single_user_mode:
                self._assign_global_entity(self.single_user_mode)

    def _after_request(self, response):
        """Add the link header to the response if the entity is set"""
        if hasattr(g, 'entity'):
            link = '<{}>; rel="https://tent.io/rels/profile"'.format(
                url_for('entity.profiles', _external=True))
            response.headers['Link'] = link
        return response
    
    def _url_defaults(self, endpoint, values):
        """Adds the entity to calls to url_for if it has been set"""
        if self.url_map.is_endpoint_expecting(endpoint, 'entity'):
            if 'entity' not in values and hasattr(g, 'entity'):
                values['entity'] = g.entity

    def validation_error(self, error):
        """Handle validation errors from the DB."""
        __tracebackhide__ = True
        
        exception = RequestDidNotValidate(validation_errors=error.errors)

        if self.config['TRAP_HTTP_EXCEPTIONS']:
            raise exception

        return exception.get_response()

def create_app(config=None):
    """Create an instance of the tentd flask application"""    
    app = TentdFlask('tentd')

    # Load the default configuration values
    app.config.update({
        'MONGODB_DB': 'tentd',
    })
    
    # Load the user configuration values
    app.config.update(make_config(config))

    @app.route('/')
    def home():
        """Returns information about the server"""
        return jsonify({'description': description, 'version': version})

    @app.route('/coffee')
    def coffee():
        raise ImATeapot

    # Initialise the db for this app
    db.init_app(app)

    # Register the blueprints
    app.register_entity_blueprint(entity)
    app.register_entity_blueprint(followers)
    app.register_entity_blueprint(posts)
    app.register_entity_blueprint(groups)
    
    return app
