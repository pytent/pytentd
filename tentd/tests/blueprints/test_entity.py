"""Tests for the entity blueprint"""

from flask import current_app, g
from py.test import mark, raises
from werkzeug.exceptions import NotFound

from tentd.documents.entity import Entity, Follower
from tentd.documents.profiles import CoreProfile, GenericProfile
from tentd.tests import GET, HEAD, profile_url_for, response_has_link_header

def test_404_on_absent_entity(app):
    """Test that profile pages for entities that don't exist 404"""
    with raises(NotFound):
        assert GET('/souffle-girl/profile')

@mark.usefixtures('app', 'entity')
class TestProfileBlueprint:
    def test_entity_link_header(self, entity):
        """Test that the entity header attached to the profile is correct"""
        assert response_has_link_header(HEAD('entity.profiles'))

    def test_profile_json(self):
        """Test that /profile returns a json document"""
        assert GET('entity.profiles').mimetype == 'application/json'
        assert GET('entity.profiles').json()

    def test_core_profile_json(self, entity):
        """Test that /profile returns an accurate core profile"""
        core_profile = GET('entity.profiles').json()[CoreProfile.__schema__]
        assert core_profile['entity'] == entity.core.identity
        assert core_profile['servers'] == entity.core.servers
        assert core_profile['tent_version'] == '0.2'

    def test_single_profile(self, entity):
        """Test that getting a single profile works"""
        core_profile = GET(
            'entity.profile', secure=True, schema=CoreProfile.__schema__)
        assert core_profile.json() == entity.core.to_json()
