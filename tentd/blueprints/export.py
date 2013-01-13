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

@export.route('/<string:name>')
def export_all(name):
    """Returns information about the server"""
    entity = Entity.objects.get_or_404(name=name)

    json = entity.to_json()
    json['followers'] = list(Follower.objects(owner=entity))
    
    return jsonify(json)
