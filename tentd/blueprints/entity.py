""" The entity endpoint """

from flask import Blueprint, jsonify, json

from tentd.models import db
from tentd.models.entity import Entity, CoreProfile, BasicProfile

entity = Blueprint('entity', __name__, url_prefix='/<string:entity>')

@entity.url_value_preprocessor
def fetch_entity (endpoint, values):
	"""	Replace `entity` (which is a string) with the actuall entity """
	values['entity'] = Entity.query.filter_by(name=values['entity']).first_or_404()

@entity.route('/profile', endpoint='profile')
def profile (entity):
	""" Return the info types belonging to the entity """
	db.session.add(entity)

        return jsonify({
		'https://tent.io/types/info/core/v0.1.0': entity.core.__json__(),
		'https://tent.io/types/info/basic/v0.1.0':{},
	})

@entity.route('/followers', endpoint='followers')
def profile(entity): 
    if(request.method == "POST"):
        pass
