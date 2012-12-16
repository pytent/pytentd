"""An implementation of the http://tent.io server protocol."""

__all__ = ["__version__", "__tent_version__", "create_app"]

__version__ = "0.0.0"
__tent_version__ = '0.2'

from flask import Flask

from tentd.blueprints.base import base
from tentd.blueprints.entity import entity
from tentd.models import db

def create_app (config=dict()):
    """ Create an instance of the tentd flask application """
    app = Flask('tentd')
    
    # Load configuration
    import tentd.defaults
    app.config.from_object(defaults)
    app.config.update(config)

    # Register the blueprints
    app.register_blueprint(base)
    app.register_blueprint(entity)

    # Initialise the db for this app
    db.init_app(app)
    db.create_all(app=app)
    
    return app
