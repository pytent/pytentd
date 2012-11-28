""" The flask application """

from __future__ import absolute_import

from flask import Blueprint, jsonify

from tentd import __doc__ as info, __version__

base = Blueprint('base', __name__)

@base.route('/')
def the_docstring ():
	return jsonify(info=info, version=__version__)