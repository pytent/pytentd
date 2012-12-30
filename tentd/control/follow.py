''' Controls the following of entities. '''
import re

import requests
from requests import ConnectionError

from flask import request
#from flask.exceptions import JSONHTTPException, JSONBadRequest

from tentd.errors import TentError

from tentd.models import db
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
        response = requests.head(identity)
    except (ConnectionError) as ex:
        raise TentError("Could not discover entity ({})".format(ex), 404)

    # TODO: 404 is probably the wrong error code
    if not 'Link' in response.headers:
        raise TentError("Entity '{}' has no Link header".format(identity), 404)
    else:
        link = response.headers['Link']

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

    # A slight bit of recursion here. Hopefully it'll never come to fruition
    if canonical_identity != url:
        pass # recurses infinitely.
#       return discover_entity(canonical_identity)

    return profile
    
def start_following(details):
    """ Peform all necessary steps to allow an entity to start follow the 
    current entity.
    This involves:
    - Performing discovery on the entity wishing to follow the current entity.
    - Making a GET request to the specified notification path which must return 200 OK.
    - Creating a relationship in the DB.
    - Returning the relationship in JSON. """

    profile = discover_entity(details['entity'])
    
    notify_resp = notify_following(profile, 
        details['notification_path'])

    if notify_resp == 200:
        follower = Follower(
            identity = profile[CoreProfile.__schema__]['entity'],
            permissions = {'public': True}, 
            licenses = details['licences'],
            types = details['types'],
            notification_path = details['notification_path'])
        db.session.add(follower)
        db.session.commit()
        return follower.to_json()
    raise TentError("Could not notify to {}/{}".format(
        profile[CoreProfile.__schema__]['entity'],
        details['notification_path']), notify_resp)

def notify_following(profile, notification_path):
    """Perform the GET request to the new follower's notification path.
    
    It should return 200 OK if it's acceptable."""
    # TODO: Adding a / is a potential bug.
    #       We may have to strip all identities of trailing /'s
    api_root = profile[CoreProfile.__schema__]['servers'][0]

    if not api_root[-1] == '/':
       api_root += '/'
    
    return requests.get(api_root + notification_path).status_code

def stop_following(follower_id):
    ''' Stops following a user. '''
    db.session.delete(get_follower(follower_id))
    db.session.commit()

def update_follower(follower_id, details):
    ''' Changes the way in which a user is followed. '''
    follower = get_follower(follower_id)

    # Set the new values.
    if 'entity' in details:
        profile = discover_entity(details['entity'])
        follower.identity = profile[CoreProfile.__schema__]['entity']

    if 'permissions' in details:
        follower.permissions = details['permissions']

    if 'licenses' in details:
        follower.licenses = details['licenses']

    if 'types' in details:
        follower.types = details['types']

    if 'notification_path' in details:
        follower.notifcation_path = details['notification_path']

    # Do the update
    follower = db.session.merge(follower)
    db.session.commit()

    return follower
    
def get_follower(follower_id):
    ''' Gets details for a followed user. '''
    follower = Follower.query.get(follower_id)

    if not follower:
        raise TentError("Follower {} does not exist.".format(follower_id), 404)

    return follower

def get_followers():
    ''' Gets the ids of all users being followed. '''
    pass

