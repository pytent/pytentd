""" The flask application """

from flask import Blueprint, jsonify

from tentd import __version__, __doc__ as info

base = Blueprint('base', __name__)

@base.route('/')
def the_docstring ():
	return jsonify(info=info, version=__version__)
