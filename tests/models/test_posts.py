# coding=utf-8
"""Test cases for posts"""

from __future__ import unicode_literals

from datetime import datetime

import tests

from tentd import db
from tentd.models.entity import Entity
from tentd.models.posts import Post, GenericPost, Status, Essay, Repost

class PostTest (tests.AppTestCase):
    def before (self):
        self.entity = Entity(name="Test")
        self.post = Status(
            entity=self.entity,
            published_at='now',
            text="Hello world")
        db.session.add(self.entity)
        db.session.add(self.post)
        db.session.commit()
    
    def test_post_owner(self):
        self.assertIn(self.post, self.entity.posts)
        self.assertEquals(self.post.entity, self.entity)
    
    def test_published_time(self):
        self.assertIsInstance(self.post.published_at, datetime)

class GenericPostTest(tests.AppTestCase):
    def before(self):
        self.entity = Entity(name="Test")
        self.post = GenericPost(
            entity=self.entity,
            schema="https://tent.io/types/post/example/v0.0.0",
            content={'attr': 'value'})
        self.commit(self.entity, self.post)

    def test_attributes(self):
        assert 'attr' in self.post.content

    def test_json(self):
        assert 'attr' in self.post.to_json()['content']

class StatusTest(tests.AppTestCase):
    def before(self):
        self.status = Status(text="Hello world", published_at='now')
        db.session.add(self.status)
        db.session.commit()
        
    def test_status(self):
        post = Post.query.all()[0]
        self.assertEquals(post, self.status)
        self.assertIsInstance(post, Status)
    
    def test_status_content(self):
        self.assertIn('text', self.status.to_json()['content'])
        
class EssayTest(tests.AppTestCase):
    def test_create_essay (self):
        essay = Essay(
            title="This is an essay post ⛺",
            body="""
This is a essay post, intended for longer texts.
Unlike a status post there is no limit on size.

However, I don't have much to write.

This is a unicode tent symbol: ⛺.
""".strip())
        db.session.add(essay)
        db.session.commit()

class RepostTest(tests.AppTestCase):
    def before(self):
        self.entity = Entity(name="Reposted")
        self.post = Status(entity=self.entity, text="This will be reposted.")

        self.repost_entity = Entity(name="Reposter")
        self.repost = Repost(
            entity=self.repost_entity,
            original_entity=self.entity,
            original_post=self.post
        )

        for i in (self.entity, self.post, self.repost_entity, self.repost):
            db.session.add(i)
        db.session.commit()

    def test_repost (self):
        self.assertEquals(self.entity, self.repost.original_entity)
        self.assertEquals(self.post, self.repost.original_post)
