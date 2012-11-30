""" The flask application """

from flask import Blueprint, jsonify, request, make_response, url_for

from tentd import __version__, __doc__ as info
from tentd.models import db
from tentd.models.entity import Entity

base = Blueprint('base', __name__)

@base.route('/')
def the_docstring ():
	return jsonify(info=info, version=__version__)

@base.route('/<username>', methods=['HEAD'])
def get_user (username):
        print username
	user = Entity.query.filter_by(url=username).first_or_404()
	resp = make_response()
	resp.headers['Link'] = url_for('.profile', username=username, _external=True)
	return resp

@base.route('/<username>/profile', methods=['GET'])
def profile (username):
	user = Entity.query.filter_by(url=username).first_or_404()
	return jsonify(user.__json__())
