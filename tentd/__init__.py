""" An implementation of the http://tent.io server protocol. """

__version__ = "0.0.0"

import os
import signal

from argparse import ArgumentParser
from flask import Flask, Config
from daemonize import Daemonize

from tentd import defaults
from tentd.blueprints.base import base
from tentd.blueprints.entity import entity
from tentd.models import db
from tentd.models.entity import Entity

tent_version = '0.2'

def create_app (config=dict()):
    """ Create an instance of the tentd flask application """
    app = Flask('tentd')
    # Load configuration
    app.config.from_object(defaults)
    app.config.update(config)
    # Register the blueprints
    app.register_blueprint(base)
    app.register_blueprint(entity)
    # Initialise the db for this app
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
    parser.add_argument("-k", "--killdaemon", action="store_true",
                help="If a daemon process is running, kill it off")
    parser.add_argument("-d", "--daemonize", action="store_true",
                help="Run the server in the background")

    # Flask configuration
    parser.add_argument("--debug", action="store_true",
        help="run flask in debug mode")

    parser.add_argument('--testing', action='store_true',
        help='run flask in testing mode')

    parser.add_argument('--dev', action='store_true',
        help='--debug and --testing')

    parser.add_argument('--db-echo', action='store_true',
        help='echo database actions')

    args = parser.parse_args()
    config = Config(os.getcwd())

    # Set the configuration options from the file given
    if args.conf:
        config.from_pyfile(args.conf)

    # Load the rest of the arguments, overriding the conf file
    config['DEBUG'] = args.debug or args.dev
    config['TESTING'] = args.testing or args.dev
    config['SQLALCHEMY_ECHO'] = args.db_echo
    
    # Create the application and create the database
    app = create_app(config)
    db.create_all(app=app)
    
    if args.show:
        from pprint import pprint
        pprint(dict(app.config))


        pidfile = "/tmp/pytentd.pid"

        if args.killdaemon:
        
            if( os.path.isfile(pidfile)):
                print "Killing pytentd"
                
                with open(pidfile,'r') as filepointer:
                    pid = filepointer.read()

                os.kill(int(pid), signal.SIGTERM)
            else:
                print "No process to kill"
         

        if args.daemonize:

            if( os.path.isfile( pidfile )):
                print "Already running server. Exiting..."

            else:
                daemon = Daemonize(app="pytentd", pid=pidfile, action=app.run)
                daemon.start()

    if not args.norun and not args.daemonize and not args.killdaemon:
        app.run()
