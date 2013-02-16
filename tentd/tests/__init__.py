"""Pytentd test suite"""

from flask import current_app, g
from py.test import main

from tentd.tests.http import *
from tentd.tests.mock import *

def profile_url_for(entity, _external=False):
    """Get an entity profile url without using url_for"""
    
    if current_app.use_subdomains:
        base_url = 'http://{user}.{server}'
    else:
        if _external:
            base_url = 'http://{server}'
        else:
            base_url = ''

        if not current_app.single_user_mode:
            base_url += '/{user}'

    server = current_app.config.get('SERVER_NAME')
    return (base_url + '/profile').format(server=server, user=entity.name)

def response_has_link_header(response):
    """Test that a response includes an entity link header"""
    link = '<{}>; rel="https://tent.io/rels/profile"'.format(
        profile_url_for(g.entity, _external=True))
    return response.headers['Link'] == link

if __name__ == '__main__':
    main()
