"""Pytentd test suite"""

from flask import current_app, g
from py.test import main

from tentd.tests.http import *
from tentd.tests.mock import *

def profile_url_for(entity, _external=False):
    """Get an entity profile url without using url_for"""
    url = ['/profile']

    if not current_app.single_user_mode:
        url.append('/' + entity.name)

    if _external:
        url.append('http://' + current_app.config['SERVER_NAME'])

    return ''.join(url[::-1])

def response_has_link_header(response):
    """Test that a response includes an entity link header"""
    link = '<{}>; rel="https://tent.io/rels/profile"'.format(
        profile_url_for(g.entity, _external=True))
    return response.headers['Link'] == link

if __name__ == '__main__':
    main()
