""" API endpoints for user interaction """

from flask import Blueprint, request, jsonify

control = Blueprint('control', __name__)

@control.route('/followers', methods=['POST'])
def followers():
	if request.json:
		return jsonify(request.json)
	elif request.data:
		return request.data
	return 'No data.'
