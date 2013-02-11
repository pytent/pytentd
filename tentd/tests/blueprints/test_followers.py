"""Tests for the entity blueprint"""

import requests

from flask import json
from py.test import raises, fixture

from tentd.documents.entity import Follower
from tentd.tests.http import POST, SPUT, SDELETE
from tentd.tests.mock import MockFunction, MockResponse
from tentd.utils.exceptions import APIBadRequest

PROFILE_FORMAT = '<{}/profile>; rel="https://tent.io/rels/profile"'

@fixture
def follower_mocks(request, monkeypatch):
    follower_identity = 'http://follower.example.com'
    follower_api_root = 'http://follower.example.com/tentd'

    monkeypatch.setattr(requests, 'head', MockFunction())

    requests.head[follower_identity] = MockResponse(
        headers={'Link': PROFILE_FORMAT.format(follower_api_root)})

    monkeypatch.setattr(requests, 'get', MockFunction())

    requests.get[follower_api_root + '/notification'] = MockResponse()
    requests.get[follower_api_root + '/profile'] = MockResponse(
        json={
            "https://tent.io/types/info/core/v0.1.0": {
                "entity": follower_identity,
                "servers": [follower_api_root],
                "licences": [],
                "tent_version": "0.2",
            }})

    assert isinstance(requests.head, MockFunction)
    assert isinstance(requests.get, MockFunction)

    @request.addfinalizer
    def teardown_mocks():
        monkeypatch.delattr(requests, 'head')
        monkeypatch.delattr(requests, 'get')

    return {
        'identity': follower_identity,
        'api_root': follower_api_root,
        'notification_path': follower_api_root + '/notification'
    }

@fixture
def new_follower_mocks(request, follower_mocks):
    new_follower_identity = 'http://changed.follower.example.com'
    new_follower_api_root = 'http://changed.follower.example.com/tentd'

    requests.head[new_follower_identity] = MockResponse(
        headers={'Link': PROFILE_FORMAT.format(new_follower_api_root)})

    requests.get[new_follower_api_root + '/notification'] = MockResponse()
    requests.get[new_follower_api_root + '/profile'] = MockResponse(
        json={
            "https://tent.io/types/info/core/v0.1.0": {
                "entity": 'http://changed.follower.example.com',
                "servers": ['http://changed.follower.example.com/tentd'],
                "licences": [],
                "tent_version": "0.2",
            }})
    
    follower_mocks.update({
        'new_identity': new_follower_identity,
        'new_api_root': new_follower_api_root,
    })
    
    return follower_mocks

def test_create_follower(entity, follower_mocks):
    """Test that you can start following an entity."""
    response = POST('followers.followers', {
        'entity': follower_mocks['identity'],
        'licences': [],
        'types': 'all',
        'notification_path': 'notification'
    })

    # Ensure the follower was created in the DB.
    Follower.objects.get(id=response.json()['id'])

    # Ensure the notification path was called
    assert requests.get.was_called(follower_mocks['notification_path'])

def test_create_invalid_follower(entity, follower_mocks):
    """Test that trying to follow an invalid entity will fail."""
    with raises(APIBadRequest):
        POST('followers.followers', '<invalid>')
    assert requests.get.was_not_called(follower_mocks['notification_path'])

def test_update_follower(entity, follower, new_follower_mocks):
    """Test that the following relationship can be edited correctly."""

    response = SPUT('followers.follower', follower_id=follower.id, data={
        'entity': new_follower_mocks['new_identity']})

    # Ensure the update happened sucessfully
    updated_follower = Follower.objects.get(id=follower.id)
    assert str(follower.id) == response.json()['id']
    assert new_follower_mocks['new_identity'] == response.json()['entity']
    assert new_follower_mocks['new_identity'] == updated_follower.identity

def test_delete_follower(follower):
    SDELETE('followers.follower', follower_id=follower.id)
    assert Follower.objects.count() == 0

def test_delete_missing_follower(entity):
    """Test that trying to stop following a non-existent user fails."""
    with raises(APIBadRequest):
        SDELETE('followers.follower', follower_id=0)
