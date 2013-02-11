# coding=utf-8
"""Test cases for posts"""

from tentd.documents import Post
from py.test import raises, mark

def test_post_owner(entity, post):
    """Assert the post has the correct owner"""
    assert post in Post.objects(entity=entity)
    assert post == Post.objects(entity=entity).first()
    assert post.entity == entity

def test_post_content(entity, post):
    """Assert the post content is the latest version"""
    post = Post.objects.get(entity=entity)
    assert post.latest.content['text'] == "Goodbye world"
    assert post.latest.content['coordinates'] == [2, 2]

def test_post_json(post):
    """Test that posts can be exported to json"""
    assert 'content' in post.to_json()

def test_post_versions(post):
    """Test that the versions are numbered correctly"""
    assert post.to_json()['version'] == 3

def test_unicode_post(entity):
    """Test that we can store unicode in posts"""
    post = Post.new(
        entity=entity,
        schema='https://tent.io/types/post/status/v0.1.0',
        content={
            'title': u"This is an essay post ⛺",
            'body': u"""
                This is a essay post, intended for longer texts.
                Unlike a status post there is no limit on size.

                This is a unicode tent symbol: ⛺

                This text does nothing.""".strip().replace('\t', '')
        })

    assert u"⛺" in post.latest.content['title']
    assert u"⛺" in post.latest.content['body']
