"""An implementation of the http://tent.io server protocol."""

__all__ = ['__version__', '__tent_version__', 'create_app']

# TODO: Are these actually used anywhere?
__version__ = '0.0.0'
__tent_version__ = '0.2'

from flask import Flask

from tentd.blueprints.base import base
from tentd.blueprints.entity import entity
from tentd.blueprints.export import export 
from tentd.models import db

def create_app(config=dict()):
    """Create an instance of the tentd flask application"""
    app = Flask('tentd')
    
    # Load configuration
    import tentd.defaults as defaults
    app.config.from_object(defaults)
    app.config.update(config)

    # Initialise the db for this app
    db.init_app(app)

    # Register the blueprints
    app.register_blueprint(base)
    app.register_blueprint(entity)
    app.register_blueprint(export)

    return app

if __name__ == '__main__':
    create_app().run(debug=True, threaded=True)