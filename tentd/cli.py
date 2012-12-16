"""Functions for running pytentd from the command line"""

import os
import signal

from argparse import ArgumentParser
from flask import Flask, Config

from tentd import create_app

parser = ArgumentParser(description=__doc__)

# Basic arguments
parser.add_argument("conf", nargs="?",
    help="a configuration file to use")
parser.add_argument("--show", action="store_true",
    help="show the configuration")

# Flask configuration
parser.add_argument("--debug", action="store_true",
    help="run flask in debug mode")

parser.add_argument('--testing', action='store_true',
    help='run flask in testing mode')

parser.add_argument('--dev', action='store_true',
    help='--debug and --testing')

parser.add_argument('--db-echo', action='store_true',
    help='echo database actions')

subparsers = parser.add_subparsers(dest="subcommand")

# Daemon mode
daemon = subparsers.add_parser('daemon', help='run pytentd as a daemon')
daemon.add_argument("--stop", "--kill", action="store_true",
    help="kill an existing daemon process")
daemon.add_argument("--start", action="store_true",
    help="run the server in the background")
daemon.add_argument("--status", action="store_true",
    help="show the status of the pytentd daemon")

subparsers.add_parser('start', help="start a pytentd server")

def run():
    """ Parse the command line arguments and run the application """
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

    if args.show:
        from pprint import pprint
        pprint(dict(app.config))
        print vars(args)

    # Manage daemon mode
    if args.subcommand == 'daemon':
        daemonize(args)

    # Run the application
    elif args.subcommand == 'start':
        app.run()

def daemonize(args):
    from daemonize import Daemonize

    def read_pid (pidfile):
        """Get the daemon's pid"""
        if os.path.isfile(pidfile):
            with open(pidfile, 'r') as f:
                return f.read().strip()
        return None

    pidfile = app.config["PIDFILE"]
    pid = read_pid(pidfile)

    # Show the status of the daemon
    if args.status:
        if pid:
            print "A pytentd daemon is already running [{}]".format(pid)
        else:
            print "No pytentd daemon is running"

    # Kill an existing daemon
    if args.stop:
        if pid:
            print "Killing existing pytentd daemon [{}]".format(pid)
            os.kill(int(pid), signal.SIGTERM)
        else:
            print "No pytentd process to kill"

    # Start pytentd in daemon mode
    if args.start:
        if not pid or args.stop:

            import logging

            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            logger.propagate = False
            fh = logging.FileHandler("/tmp/test.log", "w")
            fh.setLevel(logging.DEBUG)
            logger.addHandler(fh)
            keep_fds = [fh.stream.fileno()]

            print "Starting pytentd server"
            daemon = Daemonize(app="pytentd", pid=pidfile, action=app.run, keep_fds=keep_fds)
            daemon.start()
        else:
            print "A pytentd daemon is already running [{}]".format(pid)
