""" API endpoints for user interaction """

from flask import Blueprint, request, jsonify, json
from tentd.control import follow

control = Blueprint('control', __name__)

@control.route('/followers', methods=['POST'])
def followers():
	''' Starts following a user, defined by the post data. '''
	if request.data:
		post_data = json.loads(request.data)
		resp_data = follow.start_following(post_data)
		if resp_data: return jsonify(resp_data), 200
	return "No data", 403
