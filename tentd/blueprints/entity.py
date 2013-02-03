"""The entity endpoint"""

from datetime import datetime


from flask import json, request, g, make_response
from flask.views import MethodView

from mongoengine import ValidationError

from tentd.lib.flask import EntityBlueprint, jsonify
from tentd.utils.exceptions import APIBadRequest
from tentd.utils.auth import require_authorization
from tentd.documents import Notification
from tentd.documents.profiles import Profile, CoreProfile

entity = EntityBlueprint('entity', __name__)

@entity.route_class('/profile')
class ProfileView(MethodView):
    """The view for profile-based routes."""
    
    def get(self):
        """Return the profiles belonging to the entity"""
        return jsonify({p.schema: p.to_json() for p in g.entity.profiles})

    def post(self):
        """Create a new profile of the specified type.
        
        This is specific to pytentd, and is similar to PUT /profile/<schema>.

        TODO: Document this!
        TODO: This doesn't appear to be covered by any tests
        """
        if not 'schema' in request.json:
            raise APIBadRequest("A profile schema is required.")
        
        return jsonify(Profile(entity=g.entity, **request.json).save())

@entity.route_class('/profile/<path:schema>')
class ProfilesView(MethodView):
    """The view for individual profile-based routes."""

    @require_authorization
    def get(self, schema):
        """Get a single profile."""
        return jsonify(g.entity.profiles.get_or_404(schema=schema))

    def put(self, schema):
        """Update a profile."""
        try:
            profile = g.entity.profiles.get(schema=schema)
            profile.update_values(request.json)
        except Profile.DoesNotExist:
            profile = Profile(entity=g.entity, schema=schema, **request.json)
        return jsonify(profile.save())

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

        # Return no data other than to say the request completed correctly.
        return make_response(), 200
