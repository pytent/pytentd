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
from tentd.models.entity import Entity
from tentd.models.posts import Post, Status
