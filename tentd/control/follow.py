''' Controls the following of entities. '''
import requests, re
from requests import ConnectionError


def start_following(details):
	''' Start following a user. '''
	response = dict()
	entity = get_entity(details["entity"])

	return response

def get_entity(entity_url):
	''' Gets the actual entity details from an entity url. '''
	try:
		entity_header = requests.head(entity_url).header
		if entity_header["Link"]:
			entity = requests.get(get_entity_url(entity_header['Link']))
		else:
			return dict(error="No link header found. Not a known tentd entity.")
	except ConnectionError as e:
		return dict(error=str(e))

def get_entity_url(link_header):
	''' Helper method to get the url from the Link header. These headers are 
	typically in the form `<entity_url>; rel="type"`. '''
	temp = re.search('^<(.+)>; rel="(.+)"$').groups()
	print temp

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

