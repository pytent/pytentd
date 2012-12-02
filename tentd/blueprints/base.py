""" The flask application """

from flask import Blueprint, jsonify, url_for, make_response

from tentd import __version__, __doc__ as docstring

base = Blueprint('base', __name__)

@base.route('/')
def info ():
	"""	Returns information about the server """
	return jsonify(info=docstring, version=__version__)

@base.route('/<entity:entity>', endpoint='link', methods=['HEAD'])
def link (entity):
	"""	Returns a link to an entity's profile in the headers """
	resp = make_response()
	resp.headers['Link'] = url_for('entity.profile', entity=entity, _external=True)
	return resp
