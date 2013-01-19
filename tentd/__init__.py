"""An implementation of the http://tent.io server protocol."""

from __future__ import absolute_import

__all__ = ['create_app']

__version__ = '0.1.0'
__tent_version__ = '0.2'

from os import getcwd
from argparse import ArgumentParser

from flask import Config, Flask, jsonify

from tentd.flask import Request
from tentd.blueprints import entity, followers, posts
from tentd.documents import db

def description():
    """Returns information about the server"""
    return jsonify(description=__doc__, version=__version__)

def create_app(config=dict()):
    """Create an instance of the tentd flask application"""
    app = Flask('tentd')
    app.add_url_rule('/', 'home', description)
    app.request_class = Request
    
    # Load configuration
    import tentd.defaults as defaults
    app.config.from_object(defaults)
    app.config.update(config)

    # Initialise the db for this app
    db.init_app(app)

    # Register the blueprints
    for blueprint in (entity, followers, posts):
        app.register_blueprint(blueprint)

    return app

parser = ArgumentParser(description=__doc__)

# Basic arguments
parser.add_argument('-c', "--conf", metavar="[filename]",
    help="a configuration file to use")
parser.add_argument('-s', "--show", action="store_true",
    help="show the configuration")
parser.add_argument('-d', "--debug", action="store_true",
    help="run flask in debug mode")

def run():
    """Parse the command line arguments and run the application"""
    args = parser.parse_args()
    config = Config(getcwd())

    # Set the configuration options from the file given
    if args.conf:
        config.from_pyfile(args.conf)

    # Load the rest of the arguments, overriding the conf file
    config['DEBUG'] = args.debug

    # Create the application and create the database
    app = create_app(config)

    # Show the application config
    if args.show:
        from pprint import pprint
        pprint(dict(app.config))

    # Run the application
    app.run(threaded=app.config.get('THREADED', True))
