""" An implementation of the tent.io server protocol. """

__version__ = "0.0.0"

from flask import Flask

app = Flask('tentd')

@app.route('/')
def doc ():
	return __doc__
