"""The basic urls"""

from flask import Blueprint, jsonify, url_for, make_response

from tentd import __version__, __doc__ as docstring
from tentd.models.entity import Entity

base = Blueprint('base', __name__)

@base.route('/')
def info ():
    """Returns information about the server"""
    return jsonify(info=docstring, version=__version__)

@base.route('/<string:entity>', endpoint='link', methods=['HEAD'])
def link (entity):
    """The base API endpoint for an entity
    
    Returns a link to an entity's profile in the headers
    """
    entity = Entity.query.filter_by(name=entity).first_or_404()
    resp = make_response()
    resp.headers['Link'] = '<{0}>; rel="{1}"'.format(url_for('entity.profile', entity=entity.name, _external=True), 'https://tent.io/rels/profile')
    return resp
