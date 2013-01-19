"""The entity endpoint"""

from datetime import datetime

import requests

from flask import jsonify, json, request, url_for, g, abort
from flask.views import MethodView


from tentd.flask import Blueprint, EntityBlueprint
from tentd.control import follow
from tentd.utils.exceptions import APIBadRequest
from tentd.utils.auth import require_authorization
from tentd.documents import Entity, Post, CoreProfile, Notification

entity = EntityBlueprint('entity', __name__)

@entity.route('/profile')
def profile():
    """Return the profiles belonging to the entity"""
    return jsonify({p.schema: p.to_json() for p in g.entity.profiles})       

@entity.route_class('/profile/<path:schema>')
class ProfilesView(MethodView):
    """The view for individual profile-based routes."""

    @require_authorization
    def get(self, schema):
        """Get a single profile."""
        return jsonify(g.entity.profiles.get_or_404(schema=schema).to_json())

    def put(self, schema):
        """Update a profile."""
        profile = g.entity.profiles.get_or_404(schema=schema)

        if 'identity' in request.json:
            profile.identity = request.json['identity']
        if 'servers' in request.json:
            profile.servers = request.json['servers']

        profile.save()

        return jsonify(profile.to_json())

    def delete(self, schema):
        """Delete a profile type."""
        if schema == CoreProfile.__schema__:
            raise APIBadRequest('Cannot delete the core profile.')

        profile = g.entity.profiles.get_or_404(schema=schema)
        profile.delete()
        return '', 200

@entity.route_class('/notification', endpoint='notify')
class NotificationView(MethodView):
    def get(self):
        """Used to check the notification path is good.

        This is specific to pytentd, other tent servers may use a different
        route.

        Returns no data as it's only a check.."""
        return '', 200

    def post(self):
        """Alerts of a notification.

        This will create a new notification object in the database."""
        post_data = json.loads(request.data)

        notification = Notification()
        notification.entity = g.entity
        notification.post_id = post_data['id']
        notification.received_at = datetime.utcnow()
        notification.save()

        # Return no data other than to say the request completed correctly.
        return '', 200
