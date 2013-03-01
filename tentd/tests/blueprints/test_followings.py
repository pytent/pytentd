"""Tests for the followings blueprint"""

import requests

from flask import json
from py.test import raises, fixture, mark

from tentd.documents.entity import Following
from tentd.tests.http import GET, SGET, POST, SPOST, SDELETE
from tentd.tests.mock import MockFunction, MockResponse
from tentd.utils.exceptions import APIBadRequest

def test_get_followings(following):
    assert GET('followings.all').json()[0]['entity'] == following.identity

def test_get_following(following):
    response = SGET('followings.get', id=following.id)
    assert response.json()['entity'] == following.identity

def test_get_following_by_identity(following):
    response = SGET('followings.get_identity', identity=following.identity)
    assert response.json()['entity'] == following.identity

@mark.xfail(reason="No discovery is attempted")
def test_create_following(entity):
    identity = 'http://following.example.com'
    SPOST('followings.new', data={'entity': identity})
    following = Following.objects.get(identity=identity)

def test_delete_following(following):
    SDELETE('followings.delete', id=following.id)
    assert following not in Following.objects.all()
    