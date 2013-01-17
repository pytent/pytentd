"""The entity endpoint"""

import requests

from flask import jsonify, json, request, url_for
from flask.views import MethodView
from mongoengine import ValidationError

from tentd.flask import Blueprint
from tentd.control import follow
from tentd.utils.exceptions import APIBadRequest
from tentd.utils.auth import require_authorization
from tentd.documents.entity import Entity, Post
from tentd.documents.profiles import CoreProfile

entity = Blueprint('entity', __name__, url_prefix='/<string:entity>')

@entity.route_class('', endpoint='default')
class EntityView(MethodView):
    """The base view for entities."""

    def head(self, entity):
        """Returns the entity link header."""
        link = '<{url}>; rel="https://tent.io/rels/profile"'.format(
            url=url_for('entity.profile', entity=entity.name, _external=True))
        resp = jsonify(entity.to_json())
        resp.headers['Link'] = link
    
        return resp
        

@entity.url_value_preprocessor
def fetch_entity(endpoint, values):
    """Replace `entity` (which is a string) with the actuall entity"""
    values['entity'] = Entity.objects.get_or_404(name=values['entity'])

@entity.route_class('/profile')
class ProfileView(EntityView):
    """The view for full profile-based routes."""
    
    def get(self, entity):
        """Return the info types belonging to the entity"""
        return jsonify({p.schema: p.to_json() for p in entity.profiles})

@entity.route_class('/profile/<path:schema>')
class ProfilesView(EntityView):
    """The view for individual profile-based routes."""

    @require_authorization
    def get(self, entity, schema):
        """Gets a single type of profile if it exists."""
        return jsonify(entity.profiles.get_or_404(schema=schema).to_json()), 200

    def put(self, entity, schema):
        """Update a profile type."""
        profile = entity.profiles.get_or_404(schema=schema)
        try:
            update_data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(str(e))

        if 'identity' in update_data:
            profile.identity = update_data['identity']
        if 'servers' in update_data:
            profile.servers = update_data['servers']

        profile.save()

        return jsonify(profile.to_json()), 200

    def delete(self, entity, schema):
        """Delete a profile type."""
        if schema == CoreProfile.__schema__:
            raise APIBadRequest('Cannot delete the core profile.')

        profile = entity.profiles.get_or_404(schema=schema)
        profile.delete()
        return '', 200        

@entity.route_class('/followers')
class FollowersView(EntityView):
    """View for followers-based routes."""

    def post(self, entity):
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
    """View for follower-based routes."""
   
    @require_authorization 
    def get(self, entity, follower_id):
        """Returns the json representation of a follower"""
        return jsonify(entity.followers.get_or_404(id=follower_id).to_json())

    @require_authorization
    def put(self, entity, follower_id):
        """Updates a following relationship."""
        try:
            post_data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(str(e))
        follower = follow.update_follower(entity, follower_id, post_data)
        return jsonify(follower.to_json())

    @require_authorization
    def delete(self, entity, follower_id):
        """Deletes a following relationship."""
        try:
            follow.stop_following(entity, follower_id)
            return '', 200
        except ValidationError:
            raise APIBadRequest("The given follower id was invalid")

@entity.route_class('/notification')
class NotificationView(EntityView):
    def post(self, entity):
        """ Alerts of a notification """
        return '', 200

@entity.route_class('/posts')
class PostsView(EntityView):

    @require_authorization
    def get(self, entity):
        all_posts=[post.to_json() for post in entity.posts]
        if len(all_posts) == 0:
            return jsonify({}), 200
        return jsonify({'posts':all_posts}), 200

    @require_authorization
    def post(self, entity):
        try:
            data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(str(e))
        new_post = Post()
        new_post.entity = entity
        new_post.schema = data['schema']
        new_post.content = data['content']

        new_post.save()

        for to_notify in entity.followers:
            notification_link = follow.get_notification_link(to_notify)
            requests.post(notification_link, data=jsonify(new_post.to_json()))
            #TODO Handle failled notifications somehow

        return jsonify(new_post.to_json()), 200

@entity.route_class('/posts/<string:post_id>')
class PostsView(EntityView):
    endpoint = 'post'

    @require_authorization
    def get(self, entity, post_id):
        return jsonify(entity.posts.get_or_404(id=post_id).to_json()), 200

    @require_authorization
    def put(self, entity, post_id):
        post = entity.posts.get_or_404(id=post_id)
        try:
            post_data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise APIBadRequest(str(e))

        # TODO: Posts have more attributes than this
        
        if 'content' in post_data:
            post.content = post_data['content']
        if 'schema' in post_data:
            post.schema = post_data['schema'] 

        # TODO: Versioning.

        post.save()
        return jsonify(post.to_json()), 200

    @require_authorization
    def delete(self, entity, post_id):
        post = entity.posts.get_or_404(id=post_id)
        post.delete()
        # TODO: Notify?
        return '', 200
