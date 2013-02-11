"""Tests for the entity blueprint"""

import requests

from flask import current_app, g
from mongoengine import ValidationError
from py.test import fixture, mark, raises
from werkzeug.exceptions import NotFound

from tentd.documents.entity import Entity, Follower
from tentd.documents.profiles import CoreProfile, GenericProfile
from tentd.tests import profile_url_for, response_has_link_header
from tentd.tests.http import DELETE, GET, HEAD, PUT, POST, SPOST
from tentd.tests.mock import MockFunction, MockResponse
from tentd.utils.exceptions import APIBadRequest, RequestDidNotValidate

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

    def test_missing_single_profile(self, entity):
        """Test that getting a non-existant profile fails."""
        with raises(NotFound):
            GET('entity.profile', secure=True, schema='invalid')

    # Profile creation

    def test_create_new_profile(self, entity):
        schema = 'https://testprofile.example.com/'
        data = {'data': 'test'}

        response = PUT('entity.profile', data, secure=True, schema=schema)
        profile = entity.profiles.get(schema=schema)

        assert response.json() == profile.to_json() == data

    def test_create_invalid_profile(self, entity):
        with raises(APIBadRequest):
            PUT('entity.profile', {}, schema='<invalid>')

    @mark.xfail(reason="This can be fixed with schema checking")
    def test_create_invalid_profile_with_list(self, entity):
        with raises(APIBadRequest):
            PUT('entity.profile', ['a', 'b'], schema='<invalid>')

    # Profile updates

    def test_update_profile(self, entity):
        """Tests that a profile can be updated."""
        data = {
            'servers': [
                'http://tent.example.com',
                'http://example.com/tent',
            ]
        }

        response = PUT(
            'entity.profile', data, secure=True,
            schema=CoreProfile.__schema__)

        servers = entity.profiles.get(CoreProfile.__schema__).servers

        assert response.json()['servers'] == data['servers'] == servers

    def test_update_profile_without_data(self, entity):
        with raises(APIBadRequest):
            PUT('entity.profile', schema=CoreProfile.__schema__)

    # Profile deletion

    def test_delete_profile(self, entity):
        """Tests that a profile can be deleted."""
        schema = 'http://example.com/schema/'
        profile = GenericProfile(
            entity=entity, schema=schema, name='McTest', gender='None',
            location='Testville', avatar_url='http://example.com/avatar.jpg',
            birthdate='01/01/1980', bio='I am a test.').save()

        assert profile in entity.profiles

        DELETE('entity.profile', secure=True, schema=schema)

        assert profile not in entity.profiles

    def test_delete_core_profile(self):
        with raises(APIBadRequest):
            DELETE(
                'entity.profile', secure=True,
                schema=CoreProfile.__schema__)

    def test_delete_missing_profile(self):
        with raises(NotFound):
            DELETE(
                'entity.profile', secure=True,
                schema='http://example.com/schemas/missing')

from mock import patch

@fixture
def notification_mocks(request, follower):
    follower_api_root = follower.identity + '/tentd'
    
    head = patch('requests.head', new_callable=MockFunction)
    head.start()

    requests.head[follower.identity] = MockResponse(
        headers={'Link':
            '<{}/profile>; rel="https://tent.io/rels/profile"'\
            .format(follower_api_root)})

    get = patch('requests.get', new_callable=MockFunction)
    get.start()

    requests.get[follower_api_root + '/profile'] = MockResponse(
        json={
            "https://tent.io/types/info/core/v0.1.0": {
                "entity": follower.identity,
                "servers": [follower_api_root],
                "licences": [],
                "tent_version": "0.2"}})

    post = patch('requests.post', new_callable=MockFunction)
    post.start()
    
    requests.post[follower_api_root + '/notification'] = MockResponse()

    assert isinstance(requests.head, MockFunction)
    assert isinstance(requests.post, MockFunction)
    assert isinstance(requests.get, MockFunction)

    @request.addfinalizer
    def teardown_notification_mocks():
        head.stop()
        get.stop()
        post.stop()

    return head, get, post

@mark.usefixtures('app', 'entity', 'follower', 'notification_mocks')
class TestNotifications(object):

    def test_entity_header_notification(self):
        """Test the entity header is returned from the notifications route."""
        assert response_has_link_header(HEAD('entity.notification'))

    def test_notified_of_new_post(self, follower):
        """Test that a followers notification path has a post made to it."""        
        SPOST('posts.posts', {
            'type': 'https://tent.io/types/post/status/v0.1.0',
            'content': {
                'text': 'test',
                'location': None}})

        # TODO: Actually store the follower's servers
        follower_notification_path = follower.identity + '/tentd/notification'
        assert requests.post.was_called(follower_notification_path)

    def test_notification_created(self, entity):
        """Test that a notification is raised correctly."""
        # TODO: Test that the notification raised has the correct details.
        
        post = {
            'id': '1',
            'schema': 'https://tent.io/types/post/status/v0.1.0',
            'content': {'text': 'test', 'location': None}}

        assert entity.notifications.count() == 0

        POST('entity.notification', post)

        assert entity.notifications.count() == 1
        
