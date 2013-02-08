"""The create_app function"""

from flask import Flask, current_app, g, url_for
from mongoengine import ValidationError
from werkzeug.exceptions import ImATeapot

from tentd import __doc__ as description, __version__ as version
from tentd.lib.flask import Request, Response, JSONEncoder, jsonify
from tentd.blueprints import entity, followers, posts, groups
from tentd.documents import db, Entity
from tentd.utils import make_config


class TentdFlask(Flask):
    """An extension of the Flask class with some custom methods"""

    #: The class used for incoming requests
    request_class = Request

    #: The class used for outgoing responses
    response_class = Response

    #: Not useful until Flask 0.10
    json_encoder = JSONEncoder

    def __init__(self, *args, **kwargs):
        """Initialise the application normally and then register several
        necessary functions"""
        super(TentdFlask, self).__init__(*args, **kwargs)

        # Url handlers, mostly used to implement single user mode
        self.url_value_preprocessor(self._assign_global_entity)
        self.after_request(self._add_link_to_response)
        self.url_defaults(self._url_defaults_entity)

        # Error handlers
        self.errorhandler(ValidationError)(self._validation_error)

    @property
    def single_user_mode(self):
        """Returns the value of SINGLE_USER_MODE, defaulting to False"""
        return self.config.get('SINGLE_USER_MODE', False)

    def register_entity_blueprint(self, blueprint, **kwargs):
        """Register a blueprint with the /<entity> prefix if needed"""
        url_prefix = '' if self.single_user_mode else '/<string:entity>'
        url_prefix += blueprint.url_prefix or ''
        self.register_blueprint(blueprint, url_prefix=url_prefix, **kwargs)

    def _assign_global_entity(self, endpoint, values):
        """Assigns g.entity using app.single_user_mode or the url value"""
        if endpoint and 'entity' in values or self.single_user_mode:
            name = values.pop('entity', None) or self.single_user_mode
            g.entity = Entity.objects.get_or_404(name=name)

    def _add_link_to_response(self, response):
        """Add the link header to the response if the entity is set"""
        if hasattr(g, 'entity'):
            link = '<{}>; rel="https://tent.io/rels/profile"'.format(
                url_for('entity.profile', _external=True))
            response.headers['Link'] = link
        return response

    def _url_defaults_entity(self, endpoint, values):
        """Adds the entity to calls to url_for if it has been set"""
        if self.url_map.is_endpoint_expecting(endpoint, 'entity'):
            if 'entity' not in values and hasattr(g, 'entity'):
                values['entity'] = g.entity

    def _validation_error(self, error):
        """Handle validation errors from the DB."""
        return jsonify({'error': "Could not validate data ({}: {})".format(
            error.__class__.__name__, error.message)}), 400


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
