"""The entity endpoint"""

from flask import Blueprint, jsonify, json, g

from tentd.control import follow
from tentd.errors import TentError
from tentd.models.entity import Entity

entity = Blueprint('entity', __name__, url_prefix='/<string:entity>')

@entity.url_value_preprocessor
def fetch_entity(endpoint, values):
    """Replace `entity` (which is a string) with the actuall entity"""
    entity = Entity.query.filter_by(name=values['entity']).first_or_404()
    values['entity'] = entity
    g.entity = entity

@entity.route('/profile')
def profile(entity):
    """Return the info types belonging to the entity"""
    return jsonify({p.schema: p.to_json() for p in entity.profiles})

@entity.route('/followers', methods=['POST'])
def followers(entity):
    """Starts following a user, defined by the post data"""
    if not request.data:
        return jsonify({'error': "No POST data."}), 400

    post_data = json.loads(request.data)
    try:
        follower = follow.start_following(post_data)
        return jsonify(follower), 200
    except TentError as e:
        return jsonify(dict(error=e.reason)), e.status
