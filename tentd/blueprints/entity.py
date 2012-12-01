""" The entity endpoint """

from functools import wraps

from flask import Blueprint, jsonify, url_for, make_response

from tentd.models import db
from tentd.models.entity import Entity

class EntityBlueprint (Blueprint):
	def __init__ (self, *args, **kwargs):
		kwargs['url_prefix'] = kwargs.get('url_prefix', '') + '/<string:name>'
		super(EntityBlueprint, self).__init__(*args, **kwargs)
		
	def route (self, *args, **kwargs):	
		return super(EntityBlueprint, self).route(*args, **kwargs)

def fetch_entity (func):
	@wraps(func)
	def decorator (name, **kwargs):
		entity = Entity.query.filter_by(name=name).first_or_404()
		return func(entity=entity, **kwargs)
	return decorator

entity = EntityBlueprint('entity', __name__)

@entity.route('/', endpoint='link', methods=['HEAD'])
@fetch_entity
def get_user (entity):
	resp = make_response()
	resp.headers['Link'] = url_for('.profile', name=entity.name, _external=True)
	return resp

@entity.route('/profile', endpoint='profile')
@fetch_entity
def profile (entity):
	return jsonify(entity.__json__())
