"""
Data model for tent entities
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from tentd.models import db

class Entity (db.Model):
	"""	A tent entity """
	
	#: The local identifier and primary key
	id = Column(Integer, primary_key=True, nullable=False)
	
	#: The url identifier
	name = Column(String(20), unique=True)
	
	#: Posts made by the entity
	posts = db.relationship('Post', back_populates='owner')

        #link to core profile
        core = db.relationship('CoreProfile',backref='entity',uselist=False)
	
	def __repr__ (self):
		return "<{} '{}' [{}]>".format(self.__class__.__name__, self.name, self.id)
	
	def __str__ (self):
		"""	Used in urls, so don't change! """
		return self.name

class CoreProfile (db.Model):
	"""
	This model provides the Core Profile info type.
	
	https://tent.io/docs/info-types#core
	
		Every Tent user needs a profile with the Core info type. This block
		provides critical information that tells other servers and users how to
		interact with it.
	
	TODO: Add licence and server relationships
	"""
	
	id = Column(Integer, ForeignKey('entity.id'), primary_key=True)

	#: The canonical entity url
	url = Column(String, unique=True)

	def __json__(self):
		return {
			'entity': self.url,
			'licences': [],
			'servers': [],
		}
	
class BasicProfile (db.Model):
	"""
	The Basic Profile info type.
	
	https://tent.io/docs/info-types#basic
	
		The Basic Profile helps humanize users. All fields are optional but help
		provide a context in which to place a user's details.
	"""
	
	id = Column(Integer, ForeignKey('entity.id'), primary_key=True)

	avatar_url = Column(String)

	name       = Column(String)
	location   = Column(String)
	gender     = Column(String)
	
	birthdate  = Column(String)
	bio        = Column(Text)

	def __json__ (self):
		return {name: getattr(self, name) for name in [
			'avatar_url',
			'name',
			'location',
			'gender',
			'birthdate',
			'bio'
		]}
class Server (db.Model):
	""" A server """
	id = Column(String, primary_key=True)

class License (db.Model):
	""" A license that content is released under """
	id = Column(String, primary_key=True)

class Follower (db.Model):
	""" A follower is an entity subscribed to the posts of another entity """
	id = Column(String, primary_key=True)

class Post (db.Model):
	"""
	A post beloning to an entity.
	
	Posts are at the core of Tent. Posts are sent to followers immediately after
	being created. The tent specifcation defines that there are two ways of
	accessing posts:

	`GET posts/` returns all posts, the parameters of the request define any
	filtering. There may need to be extra filtering for server-side performance.

	`GET posts/<id>` returns a post with the defined id.
	
	Valid post content types include:
	 - status: a short (<256 character) message.
	 - essay: a longer message.
	 - photo: an image.
	 - album: a collection of photos.
	"""

	id = Column(Integer, primary_key=True)	
	
	owner_id = Column(Integer, ForeignKey('entity.id'))
	owner = relationship('Entity', back_populates='posts')

	content_type = Column(String(20))

	# The content associated with this post
	# FIXME: This should be a foriegn key to the content type
	content = Column(Text)
