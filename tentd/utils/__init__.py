"""Miscellaneous utilities for pytentd"""

from datetime import datetime
from time import mktime

# TODO: Test these

def json_attributes(obj, *items):
    json = {}
    for item in items:
        if isinstance(item, tuple):
            name, func = item
            json[name] = func(getattr(obj, name))
        elif isinstance(item, basestring):
            json[item] = getattr(obj, item)
        else:
            raise Exception("Unknown type passed to json_attributes")
    return json

def maybe(dictonary, name, value, func=None):
    """Adds a key and value to a dictionary, if the value is not None

    If no such attribute exists, the function does nothing.

    :Parameters:
    - dictionary (dict): The dictionary to add to
    - name (str): The name of the key
    - value: The value
    - func: A callable that will be used to modify the value (optional)
    """
    if value is not None:
        dictonary[name] = func(value) if func is not None else value

def time_to_string(time_field):
    """Converts a datetime instance to a string"""
    return mktime(time_field.timetuple())