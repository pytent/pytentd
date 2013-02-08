"""Follower endpoints"""

from datetime import datetime

from flask import json, request, g, make_response
from flask.views import MethodView
from mongoengine import ValidationError

from tentd.control import follow
from tentd.lib.flask import EntityBlueprint, jsonify
from tentd.utils.auth import require_authorization
from tentd.utils.exceptions import APIBadRequest
from tentd.documents import Notification

followers = EntityBlueprint('followers', __name__, url_prefix='/followers')


@followers.route_class('')
class FollowersView(MethodView):
    """View for followers-based routes."""

    def post(self):
        """Starts following a user, defined by the post data"""
        return jsonify(follow.start_following(g.entity, request.json()))


@followers.route_class('/<string:follower_id>')
class FollowerView(MethodView):
    """View for follower-based routes."""

    decorators = [require_authorization]

    def get(self, follower_id):
        """Returns the json representation of a follower"""
        return jsonify(g.entity.followers.get_or_404(id=follower_id))

    def put(self, follower_id):
        """Updates a following relationship."""
        return jsonify(follow.update_follower(
            g.entity, follower_id, request.json()))

    def delete(self, follower_id):
        """Deletes a following relationship."""
        try:
            follow.stop_following(g.entity, follower_id)
            return make_response(), 200
        except ValidationError:
            raise APIBadRequest("The given follower id was invalid")
