""" An implementation of the http://tent.io server protocol. """

__version__ = "0.0.0"

from argparse import ArgumentParser
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from tentd.blueprints.base import base

db = SQLAlchemy()

def create_app ():
	app = Flask('tentd')
	app.config['DEBUG'] = True
	app.config['TESTING'] = True
	# app.config['SQLALCHEMY_ECHO'] = True
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
	parser.add_argument("--DEBUG", action="store_true",
		help="run flask in debug mode")
	
	args = parser.parse_args()
	
	app = create_app()
	
	if args.conf:
		app.config.from_pyfile(args.conf)
	
	app.config.from_object(args)
	
	if args.show:
		from pprint import pprint
		pprint(dict(app.config))
	
	if not args.norun:
		app.run()
