"""API endpoints for user interaction"""

from flask import Blueprint, request, url_for, make_response, jsonify, json

from tentd.control import follow
from tentd.errors import TentError
from tentd.models.entity import Entity

api = Blueprint('api', __name__)

@api.route('/<string:entity>', endpoint='link', methods=['HEAD'])
def link (entity):
    """The base API endpoint for an entity

    Returns a link to an entity's profile in the headers
    """
    entity = Entity.query.filter_by(name=entity).first_or_404()
    resp = make_response()
    resp.headers['Link'] = '<{0}>; rel="{1}"'.format(url_for('entity.profile', entity=entity.name, _external=True), 'https://tent.io/rels/profile')
    return resp

@api.route('/followers', methods=['POST'])
def followers():
    """Starts following a user, defined by the post data"""
    if not request.data:
        return jsonify({'error': "No POST data."}), 400

    post_data = json.loads(request.data)
    try:
        follower = follow.start_following(post_data)
        return jsonify(follower), 200
    except TentError as e:
        return jsonify(dict(error=e.reason)), e.status
