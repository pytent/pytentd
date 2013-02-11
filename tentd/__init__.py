"""An implementation of the http://tent.io server protocol."""

from __future__ import absolute_import

__all__ = ['create_app', 'run']
__version__ = '0.1.0'
__tent_version__ = '0.2'

from argparse import ArgumentParser

from tentd.app import create_app
from tentd.utils import make_config

parser = ArgumentParser(description=__doc__)

# Basic arguments
parser.add_argument('-c',
                    "--conf",
                    metavar="[filename]",
                    help="a configuration file to use")

parser.add_argument('-d',
                    "--debug",
                    action="store_true",
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
