""" The entity endpoint """

from functools import wraps

from flask import Blueprint, jsonify, url_for, make_response

from tentd.models import db
from tentd.models.entity import Entity

entity = Blueprint('entity', __name__, url_prefix='/<entity:entity>')

@entity.route('/', endpoint='link', methods=['HEAD'])
def get_user (entity):
	resp = make_response()
	resp.headers['Link'] = url_for('.profile', entity=entity, _external=True)
	return resp

@entity.route('/profile', endpoint='profile')
def profile (entity):
	return jsonify(entity.__json__())
