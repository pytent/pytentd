"""Test single user mode"""

from flask import url_for

from tentd.documents import CoreProfile
from tentd.tests import SingleUserTestCase

class SingleUserTests(SingleUserTestCase):
    def test_urls(self):
        """Assert urls are created correctly in single user mode"""
        assert url_for('entity.profile') == '/profile'
        assert url_for('entity.profiles', schema=CoreProfile.__schema__) == \
            '/profile/https://tent.io/types/info/core/v0.1.0'

    def test_profile(self):
        """Test that /profile works correctly in single user mode"""
        response = self.client.get(url_for('entity.profile'))
        assert CoreProfile.__schema__ in response.json()

    def test_fail(self):
        """Test that a 404 error is returned when there the entity described
        by SINGLE_USER_MODE is absent."""
        self.entity.delete()
        response = self.client.get(url_for('entity.profile'))
        self.assertStatus(response, 404)

    def test_link_header(self):
        """Test that the entity link is properly included in the headers"""
        response = self.client.get(url_for('entity.profile'))
        assert 'Link' in response.headers
        expected_header = \
            '<http://tentd.example.com/profile>; '\
            'rel="https://tent.io/rels/profile"'
        assert expected_header in response.headers['Link']
