"""Following endpoints"""

from flask import json, request, g, make_response, url_for
from flask.views import MethodView
from mongoengine import ValidationError

from tentd.documents import Following
from tentd.lib.flask import EntityBlueprint, jsonify
from tentd.utils.auth import require_authorization
from tentd.utils.exceptions import APIBadRequest

followings = EntityBlueprint('followings', __name__, url_prefix='/followings')


@followings.route('', methods=['GET'], endpoint='all')
def get_all_followings():
    # TODO: Queries - before_id, since_id, until_id, limit
    return jsonify(g.entity.followings)


@followings.route('', methods=['POST'], endpoint='new')
@require_authorization
def create_new_following():
    # TODO: Discovery?
    # TODO: Yes, discovery. This is currently almost useless.
    new_following = Following(
        entity=g.entity,
        identity=request.json()['entity']
    )
    new_following.save()
    return jsonify(new_following)


@followings.route('/<string:id>', methods=['GET'], endpoint='get')
@require_authorization
def get_following_by_id(id):
    """Returns the following"""
    return jsonify(g.entity.followings.get_or_404(id=id))


@followings.route(
    '/<path:identity>', methods=['GET'], endpoint='get_identity')
@require_authorization
def get_following_by_identity(identity):
    """Returns the following with a Content-Location header"""
    following = g.entity.followings.get_or_404(identity=identity)
    correct_url = url_for('followings.get', id=following.id)
    response = make_response(jsonify(following))
    response.headers['Content-Location'] = correct_url
    return response


@followings.route('/<string:id>', methods=['DELETE'], endpoint='delete')
@require_authorization
def delete_following(id):
    """Deletes a following"""
    g.entity.followings.get_or_404(id=id).delete(safe=True)
    return make_response(), 200   
