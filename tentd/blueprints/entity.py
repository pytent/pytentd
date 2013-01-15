"""The entity endpoint"""

from json import dumps
from flask import jsonify, json, g, request, url_for
from flask.views import MethodView
from mongoengine import ValidationError

from tentd.flask import Blueprint
from tentd.control import follow
from tentd.utils.exceptions import APIException, APIBadRequest
from tentd.documents.entity import Entity, Follower, Post

entity = Blueprint('entity', __name__, url_prefix='/<string:entity>')

@entity.route_class('')
class EntityView(MethodView):
    endpoint = 'deafult'
    def head(self, entity, **kargs):
        link = '<{url}>; rel="https://tent.io/rels/profile"'.format(
            url=url_for('entity.profile', entity=entity.name, _external=True))
        resp = jsonify(entity.to_json())
        resp.headers['Link'] = link
    
        return resp
        

@entity.url_value_preprocessor
def fetch_entity(endpoint, values):
    """Replace `entity` (which is a string) with the actuall entity"""
    values['entity'] = Entity.objects.get_or_404(name=values['entity'])

@entity.route('/profile')
def profile(entity):
    """Return the info types belonging to the entity"""
    return jsonify({p.schema: p.to_json() for p in entity.profiles})

@entity.route('/followers', methods=['POST'])
def followers(entity):
    """Starts following a user, defined by the post data"""
    try:
        post_data = json.loads(request.data)
    except json.JSONDecodeError as e:
        raise APIBadRequest(str(e))

    if not post_data:
        raise APIBadRequest("No POST data.")
    
    follower = follow.start_following(entity, post_data)
    return jsonify(follower.to_json())

@entity.route_class('/followers/<string:follower_id>')
class FollowerView(EntityView):
    endpoint = 'follower'
    
    def get(self, entity, follower_id):
        """Returns the json representation of a follower"""
        return jsonify(entity.followers.get_or_404(id=follower_id).to_json())

    def put(self, entity, follower_id):
        try:
            post_data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(str(e))
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

@entity.route_class('/posts')
class PostView(EntityView):
    endpoint = "posts"

    def get(self, entity):
        all_posts=[post.to_json() for post in entity.posts]
        if len(all_posts) == 0:
            return jsonify({}), 200
        return jsonify({'posts':all_posts}), 200

    def post(self, entity):
        try:
            data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(str(e))
        post = Post()
        post.entity = entity
        post.schema = data['schema']
        post.content = data['content']

        #TODO Notify

        post.save()
        return jsonify(post.to_json()), 200

@entity.route_class('/posts/<string:post_id>')
class PostsView(EntityView):
    endpoint = 'post'
    def get(self, entity, post_id):
        return jsonify(entity.posts.get_or_404(id=post_id).to_json()), 200
    def put(self, entity, post_id):
        post = entity.posts.get_or_404(id=post_id)
        try:
            post_data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(str(e))
       
        if 'content' in post_data:
            post.content = post_data['content']
        if 'schema' in post_data:
            post.schema = post_data['schema'] 

        #TODO Versioning.

        post.save()
        return jsonify(post.to_json()), 200
    def delete(self, entity, post_id):
        post = entity.posts.get_or_404(id=post_id)
        post.delete()
        #TODO Notify?
        return '', 200
