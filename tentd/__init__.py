"""An implementation of the http://tent.io server protocol."""

from __future__ import absolute_import

__all__ = ['create_app', 'run']

__version__ = '0.1.0'
__tent_version__ = '0.2'

from os import getcwd
from argparse import ArgumentParser

from flask import Config, Flask

from tentd.lib.flask import Request, JSONEncoder, jsonify
from tentd.blueprints import entity, followers, posts, groups
from tentd.documents import db

def description():
    """Returns information about the server"""
    return jsonify({'description': __doc__, 'version': __version__})

def make_config(filename=None):
    config = Config(getcwd())
    if filename is not None:
        config.from_pyfile(filename)
    return config

def create_app(config=None):
    """Create an instance of the tentd flask application"""
    app = Flask('tentd')
    app.add_url_rule('/', 'home', description)
    app.request_class = Request
    
    # Load the default configuration values
    import tentd.defaults as defaults
    app.config.from_object(defaults)

    # Load the user configuration values
    if isinstance(config, basestring):
        config = make_config(config)

    if not isinstance(config, dict):
        raise TypeError("Config argument must be a dict or string.")
        
    if config is not None:
        app.config.update(config)

    # Initialise the db for this app
    db.init_app(app)

    # Register the entity blueprints
    for blueprint in (entity, followers, posts, groups):
        app.register_blueprint(blueprint, url_prefix=blueprint.prefix(app))

    return app

parser = ArgumentParser(description=__doc__)

# Basic arguments
parser.add_argument('-c', "--conf", metavar="[filename]",
    help="a configuration file to use")
parser.add_argument('-d', "--debug", action="store_true",
    help="run flask in debug mode")

def run():
    """Parse command line arguments and run the application"""
    args = parser.parse_args()
    
    config = make_config(args.conf)
    config['DEBUG'] = args.debug
    
    # Create the application and create the database
    app = create_app(config)

    # Run the application
    app.run(threaded=app.config.get('THREADED', True))
