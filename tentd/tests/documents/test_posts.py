# coding=utf-8
"""Test cases for posts"""

from __future__ import unicode_literals

from tentd.documents import Post
from tentd.tests import EntityTentdTestCase

class PostTest(EntityTentdTestCase):
    def before(self):
        """Create a post with several versions"""
        self.post = Post(
            entity=self.entity,
            schema='https://tent.io/types/post/status/v0.1.0')
        self.post.new_version(content={
            'text': "Hello world",
            'coordinates': [0, 0],
        })
        self.post.new_version(content={
            'text': "How are you, world?",
            'coordinates': [1, 1],
        })
        self.post.new_version(content={
            'text': "Goodbye world",
            'coordinates': [2, 2],
        })
        self.post.save()
    
    def test_post_owner(self):
        assert self.post in Post.objects(entity=self.entity)
        assert self.post == Post.objects(entity=self.entity).first()
        assert self.post.entity == self.entity

    def test_post_content(self):
        post = Post.objects.get(entity=self.entity)
        assert post.latest.content['text'] == "Goodbye world"
        assert post.latest.content['coordinates'] == [2, 2]

    def test_post_json(self):
        """Test that posts can be exported to json"""
        assert 'content' in self.post.to_json()

    def test_post_versions(self):
        """Test that the versions are numbered correctly"""
        assert self.post.to_json()['version'] == 3

class UnicodePostTest(EntityTentdTestCase):
    def before(self):
        self.essay = Post.new(
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
        assert "⛺" in self.essay.latest.content['title']
        assert "⛺" in self.essay.latest.content['body']
