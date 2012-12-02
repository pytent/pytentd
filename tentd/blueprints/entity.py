""" The entity endpoint """

from functools import wraps

from flask import Blueprint, jsonify, url_for, make_response

from tentd.models import db
from tentd.models.entity import Entity

class EntityBlueprint (Blueprint):
	def __init__ (self, *args, **kwargs):
		kwargs['url_prefix'] = kwargs.get('url_prefix', '') + '/<string:name>'
		super(EntityBlueprint, self).__init__(*args, **kwargs)
	
	def fetch_entity_decorator (self, f):
		@wraps(f)
		def decorator (name, **kwargs):
			entity = Entity.query.filter_by(name=name).first_or_404()
			return f(entity=entity, **kwargs)
		return decorator
	
	def route(self, rule, **options):
		"""
		Like :meth:`Flask.route` but for a blueprint.
		The endpoint for the :func:`url_for` function is prefixed with the name of the blueprint.
		"""
		def decorator(f):
			if options.pop('fetch_entity', True):
				f = self.fetch_entity_decorator(f)
			endpoint = options.pop("endpoint", f.__name__)
			self.add_url_rule(rule, endpoint, f, **options)
			return f
		return decorator

print "Creating blueprint"

entity = EntityBlueprint('entity', __name__)

@entity.route('/', endpoint='link', methods=['HEAD'])
def get_user (entity):
	resp = make_response()
	resp.headers['Link'] = url_for('.profile', name=entity.name, _external=True)
	return resp

@entity.route('/profile', endpoint='profile')
def profile (entity):
	return jsonify(entity.__json__())
