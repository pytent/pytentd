"""Groups endpoints."""

from flask import json, request, g, abort, make_response
from flask.views import MethodView

from tentd.flask import EntityBlueprint, jsonify

groups = EntityBlueprint('groups', __name__, url_prefix='/groups')

@groups.route_class('')
class GroupView(MethodView):
    def get(self):
        return make_response(), 200

    def put(self):
        return make_response(), 200
