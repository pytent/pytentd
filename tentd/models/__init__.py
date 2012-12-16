"""The database models"""

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Ensure all models are loaded
import tentd.models.entity
import tentd.models.profiles
import tentd.models.posts
