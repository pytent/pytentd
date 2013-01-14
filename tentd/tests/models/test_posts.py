# coding=utf-8
"""Test cases for posts"""

from __future__ import unicode_literals

from datetime import datetime

from tentd import db
from tentd.models import Entity, Profile, CoreProfile, Post
from tentd.tests import TentdTestCase, EntityTentdTestCase

class PostTest(EntityTentdTestCase):
    def before(self):
        self.post = Post(
            entity=self.entity,
            schema='https://tent.io/types/post/status/v0.1.0',
            content={'text': "Hello world"})
        self.post.save()
    
    def test_post_owner(self):
        assert self.post in Post.objects(entity=self.entity)
        assert self.post == Post.objects(entity=self.entity).first()
        assert self.post.entity == self.entity

    def test_post_content(self):
        post = Post.objects.get(entity=self.entity)
        assert post.content['text'] == "Hello world"

    def test_post_json(self):
        assert 'content' in self.post.to_json()

class UnicodePostTest(EntityTentdTestCase):
    def before(self):
        self.essay = Post(
            entity=self.entity,
            schema='https://tent.io/types/post/status/v0.1.0',
            content={
                'title': "This is an essay post ⛺",
                'body': """
                    This is a essay post, intended for longer texts.
                    Unlike a status post there is no limit on size.

                    This is a unicode tent symbol: ⛺

                    This text does nothing.""".strip().replace('\t', '')
            })
        self.essay.save()

    def test_post_content(self):
        assert "⛺" in self.essay.content['title']
        assert "⛺" in self.essay.content['body']
