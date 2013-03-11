"""The create_app function"""

from flask import Flask, current_app, g, url_for
from flask.app import ConfigAttribute, setupmethod
from mongoengine import ValidationError
from werkzeug.exceptions import ImATeapot, NotFound

from tentd import __doc__ as description, __version__ as version
from tentd.lib.flask import Request, Response, JSONEncoder, jsonify
from tentd.blueprints import entity, followers, followings, posts, groups
from tentd.documents import db, Entity
from tentd.utils import make_config, manage_exception, deprecated
from tentd.utils.exceptions import RequestDidNotValidate


class TentdFlask(Flask):
    """An extension of the Flask class with some custom methods"""

    #: The class used for incoming requests
    request_class = Request

    #: The class used for outgoing responses
    response_class = Response

    #: Not useful until Flask 0.10
    json_encoder = JSONEncoder

    @property
    def user_mode(self):
        """Return USER_MODE as lowercase"""
        return self.config['USER_MODE'].lower()

    @property
    def user_name(self):
        """Return USER_NAME in single user mode, else None"""
        if self.user_mode == 'single':
            return self.config['USER_NAME']
        return None

def create_app(config=None):
    """Create an instance of the tentd flask application"""    
    app = TentdFlask('tentd')

    # Load the default configuration values
    app.config.update({
        'MONGODB_DB': 'tentd',
        'USER_MODE': 'multiple',
        'USER_NAME': None,
    })
    
    # Load the user configuration values
    app.config.update(make_config(config))

    # Validate the configuration
    if not app.user_mode in ('multiple', 'single', 'subdomain'):
        raise Exception(
            "USER_MODE must be one of multiple, single, subdomain")

    if app.user_mode == 'single' and app.user_name is None:
        raise Exception("USER_NAME must be set in single user mode")

    @app.route('/')
    def home():
        """Returns information about the server"""
        return jsonify({'description': description, 'version': version})

    @app.route('/coffee')
    def coffee():
        raise ImATeapot

    @app.errorhandler(ValidationError)
    @manage_exception
    def validation_error(error):
        """Raise the error when in debug mode"""
        return RequestDidNotValidate(validation_errors=error.errors)

    # Initialise the db for this app
    db.init_app(app)

    # Register the blueprints
    app.register_blueprint(entity)
    app.register_blueprint(followers)
    app.register_blueprint(followings)
    app.register_blueprint(posts)
    app.register_blueprint(groups)
    
    return app
