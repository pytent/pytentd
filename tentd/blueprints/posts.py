"""Post endpoints"""

import requests

from flask import jsonify, json, request, g, abort
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

    decorators = [require_authorization]

    def get(self):
        """Gets all posts

        TODO: This should return a list
        """
        posts = [post.to_json() for post in g.entity.posts]
        if len(posts) == 0:
            return jsonify({}), 200
        return jsonify({'posts': posts}), 200

    def post(self):
        """ Used by apps to create a new post.

        Used by other servers to notify of a mention from a non-followed
        entity.

        TODO: Separate between apps creating a new post and a notification
        from a non-followed entity.
        """
        new_post = Post()
        new_post.entity = g.entity
        new_post.schema = request.json['schema']
        new_post.content = request.json['content']

        new_post.save()

        # TODO: Do this asynchronously?
        for to_notify in g.entity.followers:
            notification_link = follow.get_notification_link(to_notify)
            requests.post(notification_link, data=jsonify(new_post.to_json()))
            # TODO: Handle failed notifications somehow

        return jsonify(new_post.to_json()), 200

@posts.route_class('/<string:post_id>', endpoint='post')
class PostsView(MethodView):

    decorators = [require_authorization]
    
    def get(self, post_id):
        return jsonify(g.entity.posts.get_or_404(id=post_id).to_json()), 200
    
    def put(self, post_id):
        post = g.entity.posts.get_or_404(id=post_id)

        # TODO: Posts have more attributes than this

        if 'content' in request.json:
            post.content = request.json['content']
        if 'schema' in request.json:
            post.schema = request.json['schema']

        # TODO: Versioning.

        post.save()
        return jsonify(post.to_json()), 200
    
    def delete(self, post_id):
        g.entity.posts.get_or_404(id=post_id).delete()
        # TODO: Create a deleted post notification post(!)
        return '', 200
