"""Follower endpoints"""

from datetime import datetime

import requests

from flask import json, jsonify, request
from flask.views import MethodView
from mongoengine import ValidationError

from tentd.control import follow
from tentd.flask import EntityBlueprint
from tentd.utils.auth import require_authorization
from tentd.utils.exceptions import APIBadRequest
from tentd.documents import Notification

followers = EntityBlueprint('followers', __name__, url_prefix='/followers')

@followers.route_class('')
class FollowersView(MethodView):
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

@followers.route_class('/<string:follower_id>')
class FollowerView(MethodView):
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
