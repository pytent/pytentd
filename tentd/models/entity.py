'''
Data model and bindings for tent users
'''

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask import jsonify

from tentd.models import db

class Entity (db.Model):
	#: The local identifier and primary key
	id = Column(Integer, primary_key=True, nullable=False)
	
	#: The url identifier
	name = Column(String(20), unique=True)
	
	#: Posts made by the entity
	posts = db.relationship('Post', back_populates='creator')
	
	def __repr__ (self):
		return "<{} '{}' [{}]>".format(self.__class__.__name__, self.name, self.id)

class EntityID (Column):
	"""
	A shorthand reference to an entity
	
	Use in a declarative model::
	
		class ExampleProfile (db.Model):
			id = EntityID()
	"""
	def __init__ (self, primary_key=True, **kwargs):
		super(EntityID, self).__init__(
			Integer, ForeignKey('entity.id'),
			primary_key=primary_key, **kwargs)
		
class CoreProfile (db.Model):
	"""
	This model provides the Core Profile info type.
	
	https://tent.io/docs/info-types#core
	
		Every Tent user needs a profile with the Core info type. This block
		provides critical information that tells other servers and users how to
		interact with it.
	
	TODO: Add licence and server relationships
	"""
	
	id = EntityID()
	
	#: The canonical entity url
	url = Column(String, unique=True)
	
	def __json__ (self):
		return {'https://tent.io/types/info/core/v0.1.0': {
			'entity': self.url,
			'licences': [],
			'servers': [],
		}}
	
class BasicProfile (db.Model):
	"""
	The Basic Profile info type.
	
	https://tent.io/docs/info-types#basic
	
		The Basic Profile helps humanize users. All fields are optional but help
		provide a context in which to place a user's details.
	"""
	
	id = EntityID()

	avatar_url = Column(String)

	name       = Column(String)
	location   = Column(String)
	gender     = Column(String)
	
	birthdate  = Column(String)
	bio        = Column(Text)
	
	def __json__ (self):
		json = super(BasicProfile, self).__json__()
		attrs = ['avatar_url', 'name', 'location', 'gender', 'birthdate', 'bio']
		attrs = {attr: getattr(self, attr) for attr in attrs}
		json.update({'https://tent.io/types/info/basic/v0.1.0': attrs})
		return json

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
