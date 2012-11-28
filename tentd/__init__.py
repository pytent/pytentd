""" An implementation of the http://tent.io server protocol. """

__version__ = "0.0.0"

from argparse import ArgumentParser
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask('tentd')
db = SQLAlchemy(app)

from tentd.blueprints.base import base
app.register_blueprint(base)

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

	# DB Echo
	parser.add_argument('--echodb', action='store_true', help='Echo Database actions.')
	
	args = parser.parse_args()
	
	if args.conf:
		app.config.from_pyfile(args.conf)
	
	app.config.from_object(args)
	
	if args.show:
		from pprint import pprint
		pprint(dict(app.config))

	if args.echodb:
		app.config['SQLALCHEMY_ECHO'] = True
		

	# Create the DB
	db.create_all()

	if not args.norun:
		app.run()
