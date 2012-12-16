"""Miscellaneous utilities for pytentd"""

def json_attributes(obj, *names):
    return {name: getattr(obj, name) for name in names}
