"""Pytentd test suite"""

from flask import current_app, g
from py.test import main

from tentd.tests.http import *
from tentd.tests.mock import *

def profile_url_for(entity, _external=False):
    """Get an entity profile url without using url_for"""

    base_url = 'http://{server}' if _external else ''

    profile_url = {
        'multiple': base_url + '/{user}',
        'single': base_url,
        'subdomain': 'http://{user}.{server}',
    }[current_app.user_mode] + '/profile'

    server = current_app.config.get('SERVER_NAME')
    
    return profile_url.format(server=server, user=entity.name)

def response_has_link_header(response):
    """Test that a response includes an entity link header"""
    link = '<{}>; rel="https://tent.io/rels/profile"'.format(
        profile_url_for(g.entity, _external=True))
    return response.headers['Link'] == link

if __name__ == '__main__':
    main()
