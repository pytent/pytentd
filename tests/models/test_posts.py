"""Test cases for posts"""

from datetime import datetime

import tests

from tentd import db
from tentd.models.entity import Entity
from tentd.models.posts import Post, Status

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

class StatusTest (tests.AppTestCase):
	def before (self):
		self.status = Status(text="Hello world", published_at='now')
		db.session.add(self.status)
		db.session.commit()
		
	def test_status (self):
		post = Post.query.all()[0]
		self.assertEquals(post, self.status)
		self.assertIsInstance(post, Status)
	
	def test_status_content(self):
		self.assertIn('text', self.status.to_json()['content'])

if __name__ == "__main__":
    tests.main()
