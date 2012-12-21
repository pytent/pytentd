''' Controls the following of entities. '''
import requests, re
from requests import ConnectionError

from flask import request
#from flask.exceptions import JSONHTTPException, JSONBadRequest

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
        link = requests.head(identity).headers['Link']
        link = requests.head(identity).headers
        print link
    except (ConnectionError, KeyError) as ex:
        raise TentError("Could not discover entity ({})".format(ex), 404)


    # TODO: deal with multiple headers
    # https://tent.io/docs/server-protocol#http-codelinkcode-header
    url = re.search('^<(.+)>; rel="https://tent.io/rels/profile"$', 
        link).group(1)

    # https://tent.io/docs/server-protocol#completing-the-discovery-process
    # TODO: Accept: application/vnd.tent.v0+json
    try:
        profile = requests.get(url).json
        if CoreProfile.__schema__ not in profile:
            # TODO: 404 is probably the wrong error code
            raise TentError("Entity does not have a core profile.", 404)
    except ConnectionError as ex:
        raise TentError("Could not fetch entity profile ({})".format(ex), 404)

    canonical_identity = profile[CoreProfile.__schema__]['entity']
    if canonical_identity != url:
        return discover_entity(canonical_identity)

    return profile
    
def start_following(details):
    """ Peform all necessary steps to allow an entity to start follow the 
    current entity.
    This involves:
    - Performing discovery on the entity wishing to follow the current entity.
    - Making a GET request to the specified notification path which must return 200 OK.
    - Creating a relationship in the DB.
    - Returning the relationship in JSON. """

    print "Trying to follow:", details['entity']
    print "Our url root is:", request.url_root
    
    profile = discover_entity(details['entity'])

    follower = Follower(
        identifier = profile[CoreProfile.__schema__]['entity'],
        permissions = {'public': True}, 
        licenses = details['licences'],
        types = details['types'],
        notification_path = details['notification_path'])

    notify_following(follower)

    return follower.to_json()

def notify_following(follower):
    """ Perform the GET request to the new follower's notification path.
    It should return 200 OK if it's acceptable. """
# TODO perform GET on the notification. Needs a notification engine.
#    notification_url = url_for(follower.notification_path)
#    request = requests.get(notification_url)
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

