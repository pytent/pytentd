"""Classes and functions that extend flask"""

from __future__ import absolute_import

from flask import Blueprint

class Blueprint(Blueprint):
    """Extends the base Flask Blueprint"""

    def route_class(self, rule, endpoint=None, **kwargs):
        """Adds a class based view to a blueprint

        The endpoint name is fetched from:
        - The endpoint argument given to route_class()
        - The endpoint attribute of the class
        - The lowercased name of the class
        """
        def decorator(cls):
            name = endpoint or getattr(cls, 'endpoint', cls.__name__.lower())
            self.add_url_rule(rule, view_func=cls.as_view(name), **kwargs)
            return cls
        return decorator
