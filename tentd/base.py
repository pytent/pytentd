""" The flask application """

from flask import Blueprint, jsonify

from tentd import app, __doc__ as info, __version__
from tentd.data import db

base = Blueprint('base', __name__)

@base.route('/')
def the_docstring ():
	return jsonify(info=info, version=__version__)
