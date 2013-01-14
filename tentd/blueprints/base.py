"""The basic urls"""

from flask import Blueprint, jsonify, url_for, make_response

from tentd import __version__, __doc__ as docstring
from tentd.documents.entity import Entity
from tentd.utils.auth import require_authorization

base = Blueprint('base', __name__)

@base.route('/')
@require_authorization
def info ():
    """Returns information about the server"""
    return jsonify(info=docstring, version=__version__)

@base.route('/<string:entity>', endpoint='link', methods=['HEAD'])
def link (entity):
    """The base API endpoint for an entity
    
    Returns a link to an entity's profile in the headers
    """
    entity = Entity.objects.get_or_404(name=entity)
    link = '<{url}>; rel="https://tent.io/rels/profile"'.format(
        url=url_for('entity.profile', entity=entity.name, _external=True))
    
    resp = make_response()
    resp.headers['Link'] = link
    return resp
