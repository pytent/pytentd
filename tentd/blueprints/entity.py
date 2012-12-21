"""The entity endpoint"""

from flask import Blueprint, jsonify, json, g, request

from tentd.control import follow
from tentd.errors import TentError, JSONBadRequest
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
    try:
        post_data = json.loads(request.data)
    except json.JSONDecodeError:
        raise JSONBadRequest()

    if not post_data:
        raise JSONException("No POST data.")
    
    try:
        follower = follow.start_following(post_data)
        return jsonify(follower), 200
    except TentError as e:
        return jsonify(dict(error=e.reason)), e.status

@entity.route('/followers/<string:follower_id>', methods=['GET', 'PUT', 'DELETE'])
def follower(entity, follower_id):
    try:
        if request.method == 'GET':
            pass
        if request.method == 'PUT':
            pass
        if request.method == 'DELETE':
            follow.stop_following(follower_id)
            return '', 200
        return "Accessing: {}".format(follower_id), 200
    except TentError as ex:
        return jsonify(dict(error=ex.reason)), ex.status

@entity.route('/notification', methods=['GET'])
def get_notification(entity):
    """ Alerts of a notification """
    return '', 200
