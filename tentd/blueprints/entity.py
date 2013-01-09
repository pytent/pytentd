"""The entity endpoint"""

from flask import Blueprint, jsonify, json, g, request

from tentd.control import follow
from tentd.errors import TentError, JSONBadRequest
from tentd.models.entity import Entity
from tentd.models.posts import Post

entity = Blueprint('entity', __name__, url_prefix='/<string:entity>')

# TODO: Rename this to APIException?
@entity.errorhandler(TentError)
def exception_handler(e):
    """Catch TentErrors and returns them as json"""
    return jsonify(dict(error=e.reason)), e.status

@entity.url_value_preprocessor
def fetch_entity(endpoint, values):
    """Replace `entity` (which is a string) with the actuall entity"""
    entity = Entity.query.filter_by(name=values['entity']).first_or_404()
    values['entity'] = entity
    g.entity = entity

@entity.route('/profile')
def profile(entity):
    """Return the info types belonging to the entity"""
    return jsonify({p.schema: p.to_json() for p in entity.profiles}), 200

@entity.route('/followers', methods=['POST'])
def followers(entity):
    """Starts following a user, defined by the post data"""
    try:
        post_data = json.loads(request.data)
    except json.JSONDecodeError:
        raise JSONBadRequest()

    if not post_data:
        raise JSONException("No POST data.")
    
    try:
        follower = follow.start_following(post_data)
        return jsonify(follower), 200
    except TentError as e:
        return jsonify(dict(error=e.reason)), e.status

@entity.route('/followers/<string:follower_id>', methods=['GET', 'PUT', 'DELETE'])
def follower(entity, follower_id):
    try:
        if request.method == 'GET':
            return jsonify(follow.get_follower(follower_id).to_json()), 200
        if request.method == 'PUT':
            try:
                post_data = json.loads(request.data)
            except json.JSONDecodeError:
                raise JSONBadRequest()
            updated_follower = follow.update_follower(follower_id, post_data)
            return jsonify(updated_follower.to_json())
        if request.method == 'DELETE':
            follow.stop_following(follower_id)
            return '', 200
        return "Accessing: {}".format(follower_id), 200
    except TentError as ex:
        return jsonify(dict(error=ex.reason)), ex.status

@entity.route('/notification', methods=['GET'])
def get_notification(entity):
    """ Alerts of a notification """
    return '', 200

@entity.route('/posts', methods=['GET', 'POST'])
def get_posts(entity):
    """ Returns all public posts. Can be scoped. """
    # TODO Filter to public posts only when that's included.
    # TODO Apply other filters included as part of the GET.
    #      We'll need to think about how we handle these filters as this is 
    #      potential unsanatised input from the user and is therefore vunerable
    #      to SQL injection attacks.
    if request.method == 'GET':
        return jsonify(entity.posts), 200
    if request.method == 'POST':
        data = json.loads(request.data)
        post = Post(data)
        db.session.add(post)
        db.session.commit()

        # TODO add in something to this affect:
        # for follower in entity.followers:
        #     follower.notify(post)
        

@entity.route('/posts/<string:post_id>', methods=['GET'])
def get_post(entity, post_id):
    """ Returns a single post with the given id. """
    post = Post.query.filter_by(id=post_id).first_or_404()
    if post in entity.posts:
        return jsonify(post), 200
    return 'Post does not belong to entity.', 404
