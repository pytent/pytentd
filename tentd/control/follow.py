''' Controls the following of entities. '''
import requests, re, time
from requests import ConnectionError

from flask import jsonify, url_for

from tentd.errors import TentError
from tentd.models.entity import Follower

def start_following(details):
	''' Start following a user. '''
	entity_url = get_entity_url_from_link_header(details['entity'])
	entity = get_entity(entity_url)

	canonical_entity_url = entity['https://tent.io/types/info/core/v0.1.0']['entity']

	if canonical_entity_url != entity_url and canonical_entity_url != details['entity']:
		entity = get_entity(canonical_entity_url)

	servers = entity['https://tent.io/types/info/core/v0.1.0']['servers']

	# TODO use entity in some to create the following identity.

	
	follower = Follower(canonical_entity_url or details['entity'], 
		{'public': True}, 
		details['licenses'],
		details['types'],
		details['notification_path'])

	notify_following(follower)

	return follower.__json__()

def get_entity(entity_url):
	''' Gets the actual entity details from an entity url. '''
	try:
		entity = requests.get(entity_url).json
		if 'https://tent.io/types/info/core/v0.1.0' not in entity:
			raise TentError('Entity does not have core profile.', 404)
		return entity		
	except ConnectionError as e:
		# TODO improve this.
		raise TentError(str(e), 404)

def get_entity_url_from_link_header(entity_url):
	''' Gets the URL of an entity from the Link header of a given URL. '''
	try:
		entity_header = requests.head(entity_url).headers
		if entity_header['Link']:
			(url, type) = re.search('^<(.+)>; rel="(.+)"$', entity_header['Link']).groups()
			return url
		else:
			raise TentError('No link header found.', 404)
	except ConnectionError as e:
		raise TentError(str(e), 404)

def notify_following(follower):
	data = {'id': follower.id,
		'entity': follower.entity,
		'action': 'create'}
	data_json = jsonify(data)

	print data_json

	notification_url = url_for(follower.notification_path)
	request = requests.post(notification_url, data=data_json)
	print request

def stop_following(follower_id):
	''' Stops following a user. '''
	pass

def update_follower(follower_id, details):
	''' Changes the way in which a user is followed. '''
	pass

def get_follower(follower_id):
	''' Gets details for a followed user. '''
	pass

def get_followers():
	''' Gets the ids of all users being followed. '''
	pass

