"""The entity endpoint"""

from flask import Blueprint, jsonify, json

from tentd.models import db
from tentd.models.entity import Entity

entity = Blueprint('entity', __name__, url_prefix='/<string:entity>')

@entity.url_value_preprocessor
def fetch_entity(endpoint, values):
    """Replace `entity` (which is a string) with the actuall entity"""
    values['entity'] = Entity.query.filter_by(name=values['entity']).first_or_404()

@entity.route('/profile', endpoint='profile')
def profile(entity):
    """Return the info types belonging to the entity"""
    return jsonify({p.schema: p.to_json() for p in entity.profiles})

@entity.route('/followers', endpoint='followers')
def profile(entity): 
    if(request.method == "POST"):
        pass
