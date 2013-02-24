"""Following endpoints"""

from flask import json, request, g, make_response
from flask.views import MethodView
from mongoengine import ValidationError

from tentd.documents import Following
from tentd.lib.flask import EntityBlueprint, jsonify
from tentd.utils.auth import require_authorization
from tentd.utils.exceptions import APIBadRequest

followings = EntityBlueprint('followings', __name__, url_prefix='/followings')


@followings.route_class('')
class FollowingsView(MethodView):
    def get(self):
        # TODO: Queries - before_id, since_id, until_id, limit
        return jsonify(g.entity.followings)

    @require_authorization
    def post(self):
        # TODO: Discovery?
        return jsonify(Following(entity=g.entity, **request.json()))


@followings.route('/<string:id>', methods=['GET'])
@require_authorization
def followings_entity(id):
    """Returns the following"""
    return jsonify(g.entity.followings.get_or_404(id=id))


@followings.route('/<path:identifier>', methods=['GET'])
@require_authorization
def followings_entity(identifier):
    """Returns the following with a Content-Location header"""
    following = g.entity.followings.get_or_404(identifier=identifier)
    response = make_response(jsonify(following))
    response.headers['Content-Location'] = './' + str(following.id)
    return response


@followings.route('/<string:id>', methods=['DELETE'])
@require_authorization
def delete(self, id):
    """Deletes a following"""
    g.entity.followings.get_or_404(id=id).delete(safe=True)
    return make_response(), 200   
