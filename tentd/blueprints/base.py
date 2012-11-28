""" The flask application """

from __future__ import absolute_import

from flask import Blueprint, jsonify, request, make_response, url_for

from flask import Flask

from tentd import __doc__ as info, __version__


base = Blueprint('base', __name__)

@base.route('/')
def the_docstring ():
	return jsonify(info=info, version=__version__)

@base.route('/<username>', methods=['HEAD'])
def get_user (username):
	resp = make_response()
	resp.headers['Link'] = url_for('.profile', username=username, _external=True)
	return resp

@base.route('/<username>/profile', methods=['GET'])
def profile (username):
	return jsonify(owner=username)
