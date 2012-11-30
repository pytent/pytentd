""" The flask application """

from flask import Blueprint, jsonify, request, make_response, url_for

from tentd import __version__, __doc__ as info
from tentd.models import db
from tentd.models.entity import Entity

base = Blueprint('base', __name__)

@base.route('/')
def the_docstring ():
	return jsonify(info=info, version=__version__)

@base.route('/<name>', methods=['HEAD'])
def get_user (name):
	user = Entity.query.filter_by(name=name).first_or_404()
	resp = make_response()
	resp.headers['Link'] = url_for('.profile', name=name, _external=True)
	return resp

@base.route('/<name>/profile', methods=['GET'])
def profile (name):
	user = Entity.query.filter_by(name=name).first_or_404()
	return jsonify(user.__json__())
