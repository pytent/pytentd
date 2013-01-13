"""The basic urls"""

from flask import Blueprint, jsonify, url_for, make_response

from tentd.models.entity import Entity, Follower

export = Blueprint('export', __name__, url_prefix='/export')

@export.route('/')
def export_all():
    """Returns information about the server"""
    return jsonify({
        'entities': [entity.to_json() for entity in Entity.objects.all()],
    })
