"""Controls the following of entities."""

import re

import requests
from flask import request

from tentd.errors import APIException
from tentd.models import db
from tentd.models.entity import Follower
from tentd.models.profiles import CoreProfile

def discover_entity(identity):
    """Find an entity from the given identity

    - Fetch the identity, giving us a list of profiles
    - Fetch a profile, giving us the entity's canonical identity url
      and api endpoints

    TODO: Move this into a generic tent module?
    """

    # TODO: Parse html for links
    # https://tent.io/docs/server-protocol#server-discovery
    try:
        response = requests.head(identity)
    except requests.ConnectionError as ex:
        raise APIException("Could not discover entity ({})".format(ex), 404)

    # TODO: 404 is probably the wrong error code
    if not 'Link' in response.headers:
        raise APIException("Entity has no 'Link' header", 404)

    link = response.headers['Link']

    # TODO: deal with multiple headers
    # https://tent.io/docs/server-protocol#http-codelinkcode-header
    url = re.search('^<(.+)>; rel="https://tent.io/rels/profile"$', 
        link).group(1)

    # https://tent.io/docs/server-protocol#completing-the-discovery-process
    # TODO: Accept: application/vnd.tent.v0+json
    try:
        profile = requests.get(url).json()
        if CoreProfile.__schema__ not in profile:
            # TODO: 404 is probably the wrong error code
            raise APIException("Entity has no core profile.", 404)
    except requests.ConnectionError as ex:
        raise APIException(
            "Could not fetch entity profile ({})".format(ex), 404)

    return profile
    
def start_following(entity, details):
    """Peform all necessary steps to allow an entity to start follow the
    current entity.
    
    This involves:
    - Performing discovery on the entity wishing to follow the current entity.
    - Making a GET request to the specified notification path which must return 200 OK.
    - Creating a relationship in the DB.
    - Returning the relationship in JSON."""

    profile = discover_entity(details['entity'])

    follower = Follower(
        entity=entity,
        identity=profile[CoreProfile.__schema__]['entity'],
        licenses=details['licences'],
        types=details['types'],
        notification_path=details['notification_path'])
    
    notify_status = notify_following(profile, follower.notification_path)

    if not notify_status == 200:
        raise APIException("Could notify to {}/{}".format(
            follower.identity,
            follower.notification_path
        ), notify_status)
    return follower.save()

def notify_following(profile, notification_path):
    """Perform the GET request to the new follower's notification path.
    
    It should return 200 OK if it's acceptable."""
    # TODO: Adding a / is a potential bug.
    #       We may have to strip all identities of trailing /'s
    api_root = profile[CoreProfile.__schema__]['servers'][0]

    if not api_root[-1] == '/':
       api_root += '/'
    
    return requests.get(api_root + notification_path).status_code

def stop_following(entity, id):
    """Stops following a user."""
    follower = Follower.objects.get(entity=entity, id=id)
    follower.delete()

def update_follower(entity, follower_id, details):
    """Changes the way in which a user is followed."""
    follower = Follower.objects.get(entity=entity, id=follower_id)

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

    return follower.save()
    
def get_follower(follower_id):
    ''' Gets details for a followed user. '''
    follower = Follower.query.get(follower_id)

    if not follower:
        raise TentError("Follower {} does not exist.".format(follower_id), 404)

    return follower

def get_followers():
    ''' Gets the ids of all users being followed. '''
    pass

