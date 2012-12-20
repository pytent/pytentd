''' Controls the following of entities. '''
import requests, re, time
from requests import ConnectionError

from flask import jsonify, url_for, request
from flask.exceptions import JSONHTTPException, JSONBadRequest

from tentd.errors import TentError
from tentd.models.entity import Follower
from tentd.models.profiles import CoreProfile

def discover_entity(identity):
    """Find an entity from the given identity

    - Fetch the identity, giving us a list of profiles
    - Fetch a profile, giving us the entity's canonical identity url
      and api endpoints
    """

    # https://tent.io/docs/server-protocol#server-discovery
    # TODO: Parse html for links
    try:
        link = requests.head(entity_url).headers['Link']
    except (ConnectionError, KeyError) as e:
        raise TentError("Could not discover entity ({})".format(e), 404)

    # TODO: deal with multiple headers
    # https://tent.io/docs/server-protocol#http-codelinkcode-header
    url = re.search('^<(.+)>; rel="https://tent.io/rels/profile"$', link).group(1)

    # https://tent.io/docs/server-protocol#completing-the-discovery-process
    # TODO: Accept: application/vnd.tent.v0+json
    try:
        profile = requests.get(entity_url).json
        if CoreProfile.__schema__ not in profile:
            # TODO: 404 is probably the wrong error code
            raise TentError("Entity does not have a core profile.", 404)
    except ConnectionError as e:
        raise TentError("Could not fetch entity profile ({})".format(e), 404)

    canonical_identity = profile[CoreProfile.__schema__]['entity']
    
def start_following(details):
    ''' Start following a user. '''

    print "Trying to follow:", details['entity']
    print "Our url root is:", request.url_root
    
    entity_url = get_entity_url_from_link_header(details['entity'])
    entity = get_entity(entity_url)

    canonical_entity_url = entity['https://tent.io/types/info/core/v0.1.0']['entity']

    if canonical_entity_url != entity_url and canonical_entity_url != details['entity']:
        entity = get_entity(canonical_entity_url)

    servers = entity['https://tent.io/types/info/core/v0.1.0']['servers']

    # TODO use entity in some to create the following identity.

    print details
    follower = Follower(
        identifier = canonical_entity_url or details['entity'], 
        permissions = {'public': True}, 
        licenses = details['licences'],
        types = details['types'],
        notification_path = details['notification_path'])

    notify_following(follower)

    return follower.to_json()

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
        'entity': follower.identifier,
        'action': 'create'}
    data_json = jsonify(data)

    #print data_json
# TODO perform notification.
#    notification_url = url_for(follower.notification_path)
#    request = requests.post(notification_url, data=data_json)
    return True

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

