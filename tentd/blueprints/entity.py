"""The entity endpoint"""

from flask import jsonify, json, g, request, url_for
from flask.views import MethodView
from mongoengine import ValidationError

from tentd.flask import Blueprint
from tentd.control import follow
from tentd.utils.exceptions import APIException, APIBadRequest
from tentd.documents.entity import Entity, Follower

entity = Blueprint('entity', __name__, url_prefix='/<string:entity>')

@entity.url_value_preprocessor
def fetch_entity(endpoint, values):
    """Replace `entity` (which is a string) with the actuall entity"""
    values['entity'] = Entity.objects.get_or_404(name=values['entity'])

@entity.route('')
def link(entity):
    link = '<{url}>; rel="https://tent.io/rels/profile"'.format(
        url=url_for('entity.profile', entity=entity.name, _external=True))

    resp = jsonify(entity.to_json())
    resp.headers['Link'] = link
    
    return resp

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
        raise APIBadRequest()

    if not post_data:
        raise APIBadRequest("No POST data.")
    
    follower = follow.start_following(entity, post_data)
    return jsonify(follower.to_json())

@entity.route_class('/followers/<string:follower_id>')
class FollowerView(MethodView):
    endpoint = 'follower'
    
    def get(self, entity, follower_id):
        """Returns the json representation of a follower"""
        return jsonify(entity.followers.get_or_404(id=follower_id).to_json())

    def put(self, entity, follower_id):
        try:
            post_data = json.loads(request.data)
        except json.JSONDecodeError:
            raise JSONBadRequest()
        updated_follower = follow.update_follower(entity, follower_id, post_data)
        return jsonify(updated_follower.to_json())

    def delete(self, entity, follower_id):
        try:
            follow.stop_following(entity, follower_id)
            return '', 200
        except ValidationError:
            raise APIBadRequest("The given follower id was invalid")

@entity.route('/notification', methods=['GET'])
def get_notification(entity):
    """ Alerts of a notification """
    return '', 200
