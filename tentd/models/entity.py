'''
Data model and bindings for tent users
'''

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask import jsonify

from tentd import db

class Entity (db.Model):
	"""
	An entity is a single user.
	The base model provides the Core Profile info type.
	
	https://tent.io/docs/info-types#core
	
		Every Tent user needs a profile with the Core info type. This block
		provides critical information that tells other servers and users how to
		interact with it.
	
	TODO: Add licence and server relationships
	"""
	
	#: The local identifier for the entity
	id = Column(Integer, primary_key=True, nullable=False)
	
	#: The canonical entity url
	url = Column(String, primary_key=True, nullable=False)
	
	#: Posts made by the entity
	# posts = db.relationship('Post', back_populates='creator')
	
	def __init__(self, url):
		self.url = url

	def beep (self):
		return jsonify({'https://tent.io/types/info/core/v0.1.0': {
			'entity': self.url,
			'licences': [],
			'servers': [],
		}})
	
class BasicProfile (db.Model):
	"""
	The Basic Profile info type.
	
	https://tent.io/docs/info-types#basic
	
		The Basic Profile helps humanize users. All fields are optional but help
		provide a context in which to place a user's details.
	"""
	
	id = db.Column(db.Integer, db.ForeignKey('entity.id'), primary_key=True)

	avatar_url = Column(String)

	name       = Column(String)
	location   = Column(String)
	gender     = Column(String)
	
	birthdate  = Column(String)
	bio        = Column(Text)
	
	def __json__ (self):
		attrs = ['avatar_url', 'name', 'location', 'gender', 'birthdate', 'bio']
		attrs = {attr: getattr(self, attr) for attr in attrs}
		return jsonify({'https://tent.io/types/info/basic/v0.1.0': attrs})

class Server (db.Model):
	'''Tent servers are the protocol core. They represent the users and maintain their data and
	relationships.'''
	id = Column(String, primary_key=True)

class License (db.Model):
	'''Licenses content is released under.'''
	id = Column(String, primary_key=True)

class Follower (db.Model):
	'''A follower is a user hosted on a remote server.'''

	id = Column(String, primary_key=True)

class Post (db.Model):
	'''Posts are at the core of Tent. Posts are sent to followers immediately after being 
	created (from the tent protocol introduction).

	The tent specifcation defines that there are two ways of accessing posts:

	`GET posts/` returns all posts, the parameters of the request define any filtering.
	There may need to be extra filtering for server-side performance (i.e. only providing a set
	number of posts to stop the server being overloaded).

	`GET posts/<id>` returns a post with the defined id.'''

	# The UUID of the post on this instance (i.e. the primary key on the DB).
	id = Column(String, primary_key=True)

	# The type this post is. Valid types are:
	# - status: a short (<256 character) message.
	# - essay: a longer message.
	# - photo: an image.
	# - album: a collection of photos.
	content_type = Column(String)

	# The content associated with this post
	#FIXME This should be a foriegn key to the content type depicted by post_type.
	content = Column(String)

	# The creator of this post.
	creator_id = Column(String, ForeignKey('entity.id'))
	creator = relationship('Entity', back_populates='posts')