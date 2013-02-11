"""Tests for the entity blueprint"""

from flask import url_for, json, current_app
from py.test import mark, raises
from werkzeug.exceptions import NotFound

from tentd.documents.entity import Post
from tentd.lib.flask import jsonify
from tentd.tests import response_has_link_header
from tentd.tests.http import *
from tentd.utils import time_to_string
from tentd.utils.exceptions import APIBadRequest

def test_link_header(post):
    """Test the entity header is returned from the posts route."""
    assert response_has_link_header(SHEAD('posts.posts'))

def test_create_post(entity):
    """Test creating a post (belonging to the current entity)"""
    data = {
        'type': 'https://tent.io/types/post/status/v0.1.0',
        'content': {
            'text': "^SoftlySplinter: Hello World"
        },
        'mentions': [
            {'entity': 'http://softly.example.com'}
        ],
    }
    response = SPOST('posts.posts', data=data)
    assert 'text' in response.json()['content']

    # Fetch the post using the database
    post_id = response.json()['id']
    created_post = entity.posts.get(id=post_id)
    assert created_post.schema == data['type']
    assert created_post.latest.content == data['content']

    # Fetch the post using the API
    response = GET('posts.posts', secure=True)
    assert 'text' in response.json()[0]['content']

def test_create_post_with_invalid_data(entity):
    """Test that attempting to create an invalid post fails."""
    with raises(APIBadRequest):
        SPOST('posts.posts', '<invalid>')

def test_get_post(post):
    """Test getting a single post works correctly."""
    assert SGET('posts.post', post_id=post.id).data == jsonify(post).data

def test_get_posts(entity, post):
    """Test that getting all posts returns correctly."""
    response = GET('posts.posts', secure=True)
    posts = jsonify([p.to_json() for p in entity.posts])
    assert response.data == posts.data

def test_update_post(post):
    """Test a single post can be updated."""
    response = SPUT('posts.post', post_id=post.id,
        data={'content': {'text': 'updated', 'location': None}})

    post = Post.objects.get(id=post.id)
    assert response.data == jsonify(post).data

def test_update_post_with_invalid_data(post):
    """Test that attempting to update an invalid post fails."""
    with raises(APIBadRequest):
        SPUT('posts.post', '<invalid>', post_id=post.id)

def test_update_missing_post(entity):
    """Test that attempting to update a non-existant post fails."""
    with raises(NotFound):
        SPUT('posts.post', {}, post_id='invalid')

def test_delete_post(entity, post):
    """Test that a post can be deleted."""
    SDELETE('posts.post', post_id=post.id)
    assert entity.posts.count() == 0

def test_delete_invalid_post(entity):
    """Test that attempting to delete a non-existant post fails."""
    with raises(NotFound):
        SDELETE('posts.post', post_id='invalid')
