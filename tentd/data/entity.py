'''
Data model and bindings for tent users
'''

from sqlalchemy import Column, String, DateTime, Text

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

	def __init__(self, name, id=None):
		self.name = name
		self.id = id or Entity._get_entity_url(self)

	@staticmethod
	def _get_entity_url (entity):
		return "http://localhost/" + entity.name.lower().replace(' ','.')

class Friend (db.Model):
	'''A friend is a user hosted on a remote server.

	Friends are users who have relationships with 
	'''
	follower_id = Column(String, primary_key=True)
