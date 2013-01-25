from mongoengine.queryset import DoesNotExist

from rfc3987 import parse as url_parse

from tentd.documents import CoreProfile, BasicProfile, GenericProfile
from tentd.utils.exceptions import APIBadRequest

def create_profile(entity, values):
    if 'schema' not in values:
        raise APIBadRequest("No profile schema defined.")
    schema = values['schema']
    if profile_exists(entity, schema):
        raise APIBadRequest(
            "Profile type '{}' already exists.".format(schema))
    if schema == CoreProfile.__schema__:
        profile = CoreProfile(**values)
    elif schema == BasicProfile.__schema__:
        profile = BasicProfile(**values)
    else:
        try:
            url_parse(schema)
        except ValueError:
            raise APIBadRequest(
                "Invalid profile type '{}'.".format(schema))
        profile = GenericProfile(**values)
        profile.schema = schema
    profile.entity = entity
    return profile

def profile_exists(entity, schema):
    try:
        entity.profiles.get(schema=schema)
        return True
    except DoesNotExist:
       return False
