""" The entity endpoint """

from functools import wraps

from flask import Blueprint, jsonify

from tentd.models import db
from tentd.models.entity import Entity, CoreProfile, BasicProfile

entity = Blueprint('entity', __name__, url_prefix='/<entity:entity>')

@entity.route('/profile', endpoint='profile')
def profile (entity):
	return jsonify({
		'https://tent.io/types/info/core/v0.1.0': {},
		'https://tent.io/types/info/basic/v0.1.0': {},
	})
