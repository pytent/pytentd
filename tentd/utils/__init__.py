"""Miscellaneous utilities for pytentd"""

from functools import wraps
from time import mktime

from flask import jsonify

def json_attributes(obj, *names, **kwargs):
    """Takes an object and a list of attribute names, and returns a dict
    mapping those attribute names to the objects attribute's of the same name.

    Attributes that return None are not included in the return dict

    Example:

        >>> class A(object):
        >>>     a = 1
        >>>     b = 1
        >>> json_attributes(A(), 'a', ('b', lambda x: x*2), c=3)
        {
            'a': 1,
            'b': 2,
            'c': 3,
        }
    
    :Parameters:
    - obj: The object to fetch the attribute's from
    - names: Each 'name' should attribute name (as a string) that will be used to fetch a value from the object. Optionally, the name can be replaced with a tuple containing a name and a function to apply to the value.
    - kwargs: Each keyword: argument pair will be added to the resulting dict
    """
    json = {}
    for item in names:
        if isinstance(item, tuple):
            name, func = item
        elif isinstance(item, basestring):
            name, func = item, None
        else:
            raise Exception("Unknown type passed to json_attributes()")

        value = getattr(obj, name)

        if value is not None:
            # Modify the value if a function has been given
            json[name] = func(value) if callable(func) else value
    json.update(kwargs)
    return json

def time_to_string(time_field):
    """Converts a datetime instance to a string"""
    return mktime(time_field.timetuple())