"""
Data model for tent entities
"""

from flask import url_for
from sqlalchemy import Column, Integer, String, Text, ForeignKey

from tentd.models import db

class Entity (db.Model):
	"""	A tent entity """
	
	#: The local identifier and primary key
	id = Column(Integer, primary_key=True, nullable=False)
	
	#: The url identifier
	name = Column(String(20), unique=True)

	# The entity's info types
	core = db.relationship('CoreProfile', backref='entity', uselist=False)
	basic = db.relationship('BasicProfile', backref='entity', uselist=False)
	
	def __init__ (self, name, create_base_info_types=True, **kwargs):
		"""
		Create an Entity instance
		
		Unless `create_base_info_types==False`, Core and Basic profiles will be
		created for the Entity. The keyword arguments `core` and `basic` can be
		used to pass arguments to the respective constructors.
		"""
		self.name = name
		if create_base_info_types:
			self.core = CoreProfile(entity=self, **kwargs.get('core', {}))
			self.basic = BasicProfile(entity=self, **kwargs.get('basic', {}))
	
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

	#: The canonical entity identifier (an url)
	identifier = Column(String, unique=True)
	
	#: The entity's servers
	servers = db.relationship('Server', backref='core')

	def __json__(self):
		# The entity's API root
		link = url_for('base.link', entity=self.entity, _external=True)
			
		return {
			'entity': self.identifier or link,
			'licences': [],
			'servers': [link],
		}

class Server (db.Model):
	""" An API root that a entities can be found at """
	url = Column(String, primary_key=True)
	
	core_id = Column(Integer, ForeignKey('core_profile.id'))
	
	def __init__ (self, url, core):
		self.url = url
		self.core = core
	
	def __repr__ (self):
		return "<Server '{}': '{}'>".format(self.core.entity.name, self.url)
	
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

class License (db.Model):
	""" A license that content is released under """
	id = Column(String, primary_key=True)

class Follower (db.Model):
	""" A follower is an entity subscribed to the posts of another entity """
	id = Column(String, primary_key=True)
