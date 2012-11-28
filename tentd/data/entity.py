'''
Data model and bindings for tent users
'''

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from tentd.data import db

class Entity (db.Model):
	""" A tent entity, better known as a user """

	id         = Column(String, primary_key=True)
	avatar_url = Column(String)

	name       = Column(String)
	location   = Column(String)
	gender     = Column(String)
	
	birthdate  = Column(DateTime)
	bio        = Column(Text)

	posts      = relationship('Post', back_populates='creator')

	def __init__(self, name, id=None):
		self.name = name
		self.id = id or Entity._get_entity_url(self)

	@staticmethod
	def _get_entity_url (entity):
		return "http://localhost/" + entity.name.lower().replace(' ','.')

class CoreProfile:
	'''The most basic tent profile which every user must have.
	
	This provides critical information that tells other servers how to interact with it.'''

	CORE_DESCRIPTOR = 'https://tent.io/types/info/core/v0.1.0'

	#FIXME Find out the best way of putting these into a DB without messing up everything.
	entity = 'String'
	licenses = []
	servers = []

class BasicProfile (CoreProfile):
	'''The Basic Profile helps humanize users. All fields are optional but help provide a 
	context in which to place a user's details.'''

	DESCRIPTOR = 'https://tent.io/types/info/basic/v0.1.0'

	#FIXME make these into columns.
	name = 'String'
	avatar_url = 'String'
	birthdate = 'Strng'
	location = 'String'
	gender = 'String'
	bio = 'String'

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
	id = Columm(String, primary_key=True)

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
