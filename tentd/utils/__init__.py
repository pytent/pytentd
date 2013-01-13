"""Miscellaneous utilities for pytentd"""

from datetime import datetime
from time import mktime

def json_attributes(obj, *names):
    return {name: getattr(obj, name) for name in names}

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