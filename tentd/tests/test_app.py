"""Test the pytentd application"""

from flask import url_for, g
from py.test import mark, raises, fixture
from werkzeug.exceptions import ImATeapot, NotFound

from tentd.documents import CoreProfile
from tentd.tests import GET

@fixture
def global_entity(app, entity):
    """Sets g.entity manually, for when a request is absent"""
    g.entity = entity

def get_profile_url(app, entity):
    """Return the expected profile url"""
    if app.single_user_mode:
        return '/profile'
    else:
        return '/{}/profile'.format(entity.name)

def test_coffee(app):
    """Test that /coffee raises an exception"""
    with raises(ImATeapot):
        assert GET('coffee')

def test_url_value_preprocessor(app, entity, global_entity):
    """Assert urls are created correctly in single user mode"""
    assert url_for('entity.profile') == get_profile_url(app, entity)

def test_url_defaults(app, entity, global_entity):
    """Assert that the url defaults are working"""
    g.entity = entity
    assert CoreProfile.__schema__ in GET('entity.profile').json()

def test_link_header(app, entity, global_entity):
    """Assert that the link header is correct"""
    expected_header = \
        '<http://tentd.example.com{}>; '\
        'rel="https://tent.io/rels/profile"'.format(
            get_profile_url(app, entity))
    assert expected_header in GET('entity.profile').headers['Link']
