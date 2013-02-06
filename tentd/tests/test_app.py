"""Test the pytentd application"""

from flask import url_for, g
from py.test import mark, raises
from werkzeug.exceptions import ImATeapot, NotFound

from tentd.documents import CoreProfile
from tentd.tests import GET

class global_entity(object):
    """Set g.entity manually, for cases where these is no current request"""
    def __init__(self, entity):
        self.entity = entity
        
    def __enter__(self):
        g.entity = self.entity

    def __exit__(self, type, value, traceback):
        del g.entity

def get_profile_url(app, entity):
    """Get an entity profile url without using url_for"""
    if app.single_user_mode:
        return '/profile'
    return '/{}/profile'.format(entity.name)

def test_url_value_preprocessor(app, entity):
    """Assert urls are created correctly in single user mode"""
    with global_entity(entity):
        assert url_for('entity.profile') == get_profile_url(app, entity)

def test_url_defaults(app, entity):
    """Assert that the url defaults are working"""
    with global_entity(entity):
        assert CoreProfile.__schema__ in GET('entity.profile').json()

def test_link_header(app, entity):
    with global_entity(entity):
        expected_header = \
            '<http://tentd.example.com{}>; '\
            'rel="https://tent.io/rels/profile"'.format(
                get_profile_url(app, entity))
        assert expected_header in GET('entity.profile').headers['Link']

def test_coffee(app):
    """Test that /coffee raises an exception"""
    with raises(ImATeapot):
        assert GET('coffee')
