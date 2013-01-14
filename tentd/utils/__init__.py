"""Miscellaneous utilities for pytentd"""

from datetime import datetime
from time import mktime

def iterable_to_json(iterable):
    """Calls ``.to_json()`` on each element of an iterable"""
    return [obj.to_json() for obj in iterable]

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