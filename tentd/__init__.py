""" An implementation of the http://tent.io server protocol. """

__version__ = "0.0.0"

from os import getcwd
from argparse import ArgumentParser
from flask import Flask, Config

from tentd.models import db
from tentd.blueprints.base import base

def create_app (config=dict()):
	app = Flask('tentd')
	app.config.update(config)
	app.register_blueprint(base)
	db.init_app(app)
	return app

def run ():
	""" Parse the command line arguments and run the application """
	parser = ArgumentParser(description=__doc__)

	# Basic arguments
	parser.add_argument("conf", nargs="?",
		help="a configuration file to use")
	parser.add_argument("--show", action="store_true",
		help="show the configuration")
	parser.add_argument("--norun", action="store_true",
		help="stop after creating the app, useful with --show")

	# Flask configuration
	parser.add_argument("--debug", action="store_true",
		help="run flask in debug mode")

	parser.add_argument('--testing', action='store_true',
		help='run flask in testing mode')
		
	parser.add_argument('--echodb', action='store_true',
		help='echo database actions')
	
	parser.add_argument('--dev', action='store_true',
		help='--debug, --testing and --echo')
	
	# Load the arguments
	args = parser.parse_args()
	
	config = Config(getcwd())
	config['DEBUG'] = args.debug or args.dev
	config['TESTING'] = args.testing or args.dev
	config['SQLALCHEMY_ECHO'] = args.echodb or args.dev

	# Set the configuration options from the file given
	if args.conf:
		config.from_pyfile(args.conf)
	
	# Create the application and create the database
	app = create_app(config)
	db.create_all(app=app)
	
	if args.show:
		from pprint import pprint
		pprint(dict(app.config))
	
	if not args.norun:
		app.run()
