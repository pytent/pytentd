''' Controls the following of entities. '''
import requests, re, time
from requests import ConnectionError


def start_following(details):
	''' Start following a user. '''
	response = dict()
	entity = get_entity(details["entity"])

	# TODO use entity in some way here.
	
	response['entity'] = details['entity']
	response['created_at'] = int(time.time())
	response['permissions'] = dict(public=True)
	response['id'] = ''
	response['licenses'] = details['licenses']
	response['types'] = details['types']
	response['notification_path'] = details['notification_path']

	return response

def get_entity(entity_url):
	''' Gets the actual entity details from an entity url. '''
	try:
		print 'HEAD {} HTTP/1.1'.format(entity_url)
		entity_header = requests.head(entity_url).headers
		if entity_header["Link"]:
			(profile_url, profile_type) = get_entity_url(entity_header['Link'])
			print "GET {} HTTP/1.1".format(profile_url)
			return requests.get(profile_url).json
		else:
			return dict(error="No link header found. Not a known tentd entity.")
	except ConnectionError as e:
		return dict(error=str(e))

def get_entity_url(link_header):
	''' Helper method to get the url from the Link header. These headers are 
	typically in the form `<entity_url>; rel="type"`. '''
	print link_header
	return re.search('^<(.+)>; rel="(.+)"$', link_header).groups()

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

