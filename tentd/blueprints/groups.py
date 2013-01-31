"""Groups endpoints."""

from flask import json, request, g, abort, make_response
from flask.views import MethodView

from tentd.flask import EntityBlueprint, jsonify
from tentd.documents import Group

groups = EntityBlueprint('groups', __name__, url_prefix='/groups')

@groups.route_class('')
class GroupsView(MethodView):
    def get(self):
        return jsonify(g.entity.groups), 200

    def post(self):
        return jsonify(Group(entity=g.entity, **request.json).save())

@groups.route_class('/<string:name>')
class GroupView(MethodView):
    def get(self, name):
        return jsonify(g.entity.groups.get_or_404(name=name).to_json())

    def put(self, name):
        return make_response(), 200

    def delete(self, name):
        return make_response(), 200
