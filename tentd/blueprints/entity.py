"""The entity endpoint"""

from datetime import datetime

from flask import jsonify, json, request, g, make_response
from flask.views import MethodView

from mongoengine.queryset import DoesNotExist

from rfc3987 import parse as url_parse

from tentd.flask import EntityBlueprint
from tentd.utils.exceptions import APIBadRequest
from tentd.utils.auth import require_authorization
from tentd.documents import CoreProfile, BasicProfile, GenericProfile, \
    Notification
from tentd.utils.profile import create_profile, profile_exists

entity = EntityBlueprint('entity', __name__)

@entity.route_class('/profile')
class ProfileView(MethodView):
    """The view for profile-based routes."""
    def get(self):
        """Return the profiles belonging to the entity"""
        return jsonify({p.schema: p.to_json() for p in g.entity.profiles})
    def post(self):
        """Create a new profile of the specified type.
        
        Specific to pytentd."""
        profile = create_profile(g.entity, request.json)
        profile.save()
        return jsonify(profile.json), 200

        

@entity.route_class('/profile/<path:schema>')
class ProfilesView(MethodView):
    """The view for individual profile-based routes."""

    @require_authorization
    def get(self, schema):
        """Get a single profile."""
        return jsonify(g.entity.profiles.get_or_404(schema=schema).to_json())

    def put(self, schema):
        """Update a profile."""
        if profile_exists(g.entity, schema):
            profile = g.entity.profiles.get(schema=schema)
            profile.update_values(request.json)
        else:
            profile_values = request.json
            profile_values['schema'] = schema
            profile = create_profile(g.entity, profile_values)

        profile.entity = g.entity
        profile.save()
        return jsonify(profile.to_json())

    def delete(self, schema):
        """Delete a profile type."""
        if schema == CoreProfile.__schema__:
            raise APIBadRequest('Cannot delete the core profile.')

        profile = g.entity.profiles.get_or_404(schema=schema)
        profile.delete()
        return make_response(), 200

@entity.route_class('/notification', endpoint='notify')
class NotificationView(MethodView):
    """Routes relating to notifications."""
    def get(self):
        """Used to check the notification path is good.

        This is specific to pytentd, other tent servers may use a different
        route.

        Returns no data as it's only a check.."""
        return make_response(), 200

    def post(self):
        """Alerts of a notification.

        This will create a new notification object in the database."""
        post_data = json.loads(request.data)

        notification = Notification()
        notification.entity = g.entity
        notification.post_id = post_data['id']
        notification.received_at = datetime.utcnow()
        notification.save()

        return make_response(), 200
