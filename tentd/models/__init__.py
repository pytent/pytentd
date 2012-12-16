"""The database models"""

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def add_and_commit (*items):
    """Commit multiple items to the db in one call"""
    for item in items:
        db.session.add(item)
    db.session.commit()

db.add_and_commit = add_and_commit

# Ensure all models are loaded
import tentd.models.entity
import tentd.models.profiles
import tentd.models.posts
