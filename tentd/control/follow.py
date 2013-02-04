"""Controls the following of entities."""

import re

import requests

from tentd.utils.exceptions import APIException, APIBadRequest
from tentd.documents.auth import KeyPair
from tentd.documents.entity import Follower
from tentd.documents.profiles import CoreProfile

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
        raise APIBadRequest("Could not discover entity ({})".format(ex))

    # TODO: 404 is probably the wrong error code
    if not 'Link' in response.headers:
        raise APIBadRequest("Entity has no 'Link' header")

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
            raise APIException("Entity has no core profile.")
    except requests.ConnectionError as ex:
        raise APIException(
            "Could not fetch entity profile ({})".format(ex))

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

    keypair = KeyPair(
        owner=follower, mac_id=keyid, mac_key=key,
        mac_algorithm="hmac-sha-256")
    
    notify_status = notify_following(follower)

    if not notify_status == 200:
        raise APIException("Could notify to {}/{}".format(
            follower.identity,
            follower.notification_path
        ), notify_status)

    return follower.save(), keypair.save()

def notify_following(follower):
    """Perform the GET request to the new follower's notification path.
    
    It should return 200 OK if it's acceptable."""
    resp = requests.get(get_notification_link(follower))
    return resp.status_code

def get_notification_link(follower):
    """Gets the absolute link of the notification path.""" 
    # TODO: Adding a / is a potential bug.
    #       We may have to strip all identities of trailing /'s

    profile = discover_entity(follower.identity)
    api_root = profile[CoreProfile.__schema__]['servers'][0]

    if api_root[-1] == '/':
        api_root = api_root[:-1]

    return api_root + '/' + follower.notification_path

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
    """Gets details for a followed user."""
    follower = Follower.query.get(follower_id)

    if not follower:
        raise APIException("Follower {} does not exist.".format(follower_id))

    return follower

def get_followers():
    """Gets the ids of all users being followed."""
    pass

