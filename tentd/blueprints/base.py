""" The flask application """

from flask import Blueprint, jsonify, url_for, make_response

from tentd import __version__, __doc__ as info

base = Blueprint('base', __name__)

@base.route('/')
def the_docstring ():
	return jsonify(info=info, version=__version__)

@base.route('/<entity:entity>', endpoint='link', methods=['HEAD'])
def get_user (entity):
	resp = make_response()
	resp.headers['Link'] = url_for('entity.profile', entity=entity, _external=True)
	return resp
