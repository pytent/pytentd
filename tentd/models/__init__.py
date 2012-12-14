"""The database models"""

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Ensure all models are loaded
from tentd.models.entity import Entity
from tentd.models.posts import Post, Status
