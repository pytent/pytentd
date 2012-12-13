""" API endpoints for user interaction """

from flask import Blueprint, request, jsonify, json
from tentd.control import follow
from tentd.errors import TentError

control = Blueprint('control', __name__)

@control.route('/followers', methods=['POST'])
def followers():
	''' Starts following a user, defined by the post data. '''
	if request.data:
		post_data = json.loads(request.data)

		try:
			resp_data = follow.start_following(post_data)
			return jsonify(resp_data), 200
		except TentError as e:
			return jsonify(dict(error=e.reason)), e.status
	return jsonify(dict(error="No POST data.")), 400
