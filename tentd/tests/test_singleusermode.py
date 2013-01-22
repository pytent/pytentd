"""Test single user mode"""

from flask import url_for

from tentd.documents import CoreProfile
from tentd.tests import SingleUserTestCase

class SingleUserTests(SingleUserTestCase):
    def test_urls(self):
        assert url_for('entity.profile') == '/profile'
        assert url_for('entity.profiles', schema=CoreProfile.__schema__) == \
            '/profile/https://tent.io/types/info/core/v0.1.0'

    def test_profile(self):
        response = self.client.get(url_for('entity.profile'))
        assert CoreProfile.__schema__ in response.json()
