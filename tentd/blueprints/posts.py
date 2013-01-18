"""Post endpoints"""

import requests

from flask import jsonify, json, request, url_for, g, abort
from flask.views import MethodView

from tentd.flask import Blueprint, EntityBlueprint
from tentd.control import follow
from tentd.utils.exceptions import APIBadRequest
from tentd.utils.auth import require_authorization
from tentd.documents import Entity, Post, CoreProfile, Notification

posts = EntityBlueprint('posts', __name__, url_prefix='/posts')

@posts.route_class('')
class PostsView(MethodView):
    """ Routes relatings to posts. """

    @require_authorization
    def get(self, entity):
        """ Gets all posts """
        all_posts=[post.to_json() for post in entity.posts]
        if len(all_posts) == 0:
            return jsonify({}), 200
        return jsonify({'posts':all_posts}), 200

    @require_authorization
    def post(self, entity):
        """ Used by apps to create a new post.

        Used by other servers to notify of a mention from a non-followed
        entity."""

        #TODO seperate between apps creating a new post and a notification from
        # a non-followed entity.
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

@posts.route_class('/<string:post_id>')
class PostsView(MethodView):
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
