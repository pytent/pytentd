"""The create_app function"""

from flask import Flask, current_app, g, url_for
from mongoengine import ValidationError

from tentd import __doc__ as description, __version__ as version
from tentd.lib.flask import Request, JSONEncoder, jsonify
from tentd.blueprints import entity, followers, posts, groups
from tentd.documents import db, Entity
from tentd.utils import make_config

class TentdFlask(Flask):
    """An extension of the Flask class with some custom methods"""
    @property
    def single_user_mode(self):
        """Returns the value of SINGLE_USER_MODE, defaulting to False"""
        return self.config.get('SINGLE_USER_MODE', False)
    
    def register_entity_blueprint(self, blueprint, **kwargs):
        """Register a blueprint with the /<entity> prefix if needed"""
        url_prefix = '' if self.single_user_mode else '/<string:entity>'
        url_prefix += blueprint.url_prefix or ''
        self.register_blueprint(blueprint, url_prefix=url_prefix, **kwargs)

def create_app(config=None):
    """Create an instance of the tentd flask application"""    
    app = TentdFlask('tentd')
    app.request_class = Request

    # Load the default configuration values
    import tentd.defaults as defaults
    app.config.from_object(defaults)
    
    # Load the user configuration values
    app.config.update(make_config(config))

    @app.route('/')
    def home():
        """Returns information about the server"""
        return jsonify({'description': description, 'version': version})

    @app.errorhandler(ValidationError)
    def validation_error(error):
        """Handle validation errors from the DB."""
        return jsonify({'error': error.to_dict()}), 400

    @app.url_defaults
    def url_default_entity(endpoint, values):
        """Adds the entity to calls to url_for if it has been set"""
        if app.url_map.is_endpoint_expecting(endpoint, 'entity'):
            if 'entity' not in values and hasattr(g, 'entity'):
                values['entity'] = g.entity

    @app.url_value_preprocessor
    def assign_global_entity(endpoint, values):
        """Assigns g.entity using app.single_user_mode or the url value"""
        if endpoint:
            name = app.single_user_mode or values.pop('entity', None)
            g.entity = Entity.objects.get_or_404(name=name)

    @app.after_request
    def profile_link_header(response):
        """Add the link header to the response if the entity is set"""
        if hasattr(g, 'entity'):
            link = '<{}>; rel="https://tent.io/rels/profile"'.format(
                url_for('entity.profile', _external=True))
            response.headers['Link'] = link
        return response
    
    # Initialise the db for this app
    db.init_app(app)

    # Register the blueprints
    app.register_entity_blueprint(entity)
    app.register_entity_blueprint(followers)
    app.register_entity_blueprint(posts)
    app.register_entity_blueprint(groups)
    
    return app
