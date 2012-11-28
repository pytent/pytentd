""" An implementation of the http://tent.io server protocol. """

__version__ = "0.0.0"

import argparse
from flask import Flask

from tentd.base import base
from tentd.run import run_application

app = Flask('tentd')
app.register_blueprint(base)

run = lambda run: run_application(app)
