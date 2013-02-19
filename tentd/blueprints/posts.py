"""Post endpoints"""

import requests

from flask import json, request, g, abort, make_response
from flask.views import MethodView

from mongoengine import Q

from tentd.lib.flask import EntityBlueprint, jsonify
from tentd.utils import follow
from tentd.utils.exceptions import APIBadRequest
from tentd.utils.auth import require_authorization
from tentd.documents import Entity, Post, CoreProfile, Notification

posts = EntityBlueprint('posts', __name__, url_prefix='/posts')

DEFAULT_POST_LIMIT = 200

@posts.route_class('', endpoint='posts')
class PostsView(MethodView):
    """ Routes relatings to posts. """

    decorators = [require_authorization]

    def get(self):
        """Gets all posts"""
        query = []
        limit = DEFAULT_POST_LIMIT
        if 'limit' in request.args:
            limit = min(int(request.args['limit']), limit)

        return jsonify(g.entity.posts(*query).limit(limit))

    def post(self):
        """ Used by apps to create a new post.

        Used by other servers to notify of a mention from a non-followed
        entity.

        TODO: Separate between apps creating a new post and a notification
        from a non-followed entity.
        """
        if not 'type' in request.json():
            raise APIBadRequest("Posts must define a schema")
        if 'received_at' in request.json():
            raise APIBadRequest("You may not set received_at on a post")

        post = Post(entity=g.entity, schema=request.json().pop('type'))
        post.new_version(**request.json())
        post.save()

        # TODO: Do this asynchronously?
        for to_notify in g.entity.followers:
            notification_link = follow.get_notification_link(to_notify)
            requests.post(notification_link, data=jsonify(post.to_json()))
            # TODO: Handle failed notifications somehow

        return jsonify(post)


@posts.route_class('/<string:post_id>', endpoint='post')
class PostsView(MethodView):

    decorators = [require_authorization]

    def get(self, post_id):
        return jsonify(g.entity.posts.get_or_404(id=post_id))

    def put(self, post_id):
        post = g.entity.posts.get_or_404(id=post_id)

        # TODO: Posts have more attributes than this
        if 'content' in request.json():
            post.content = request.json()['content']
        if 'schema' in request.json():
            post.schema = request.json()['schema']

        # TODO: Versioning.
        return jsonify(post.save())

    def delete(self, post_id):
        # TODO: Create a deleted post notification post(!)
        post = g.entity.posts.get_or_404(id=post_id)
        version_number = request.args.get('version', None)
        if version_number:
            if len(post.versions) == 1:
                raise APIBadRequest("Cannot delete a posts last version")
            del post.versions[int(version_number)]
            post.save()
        else:
            post.delete()
        return make_response(), 200


@posts.route_class('/<string:post_id>/versions', endpoint='versions')
class VersionsView(MethodView):
    decorators = [require_authorization]

    def get(self, post_id):
        return jsonify(g.entity.posts.get_or_404(id=post_id).versions)


@posts.route_class('/<string:post_id>/mentions', endpoint='mentions')
class MentionsView(MethodView):
    def get(self, post_id):
        return jsonify(
            g.entity.posts.get_or_404(id=post_id).versions[0].mentions)
