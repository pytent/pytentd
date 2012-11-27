""" The data storage backend """

from flask.ext.sqlalchemy import SQLAlchemy

from tentd import app

db = SQLAlchemy(app)

class ConfigurationException (Exception):
	def __init__(self, message, config):
		super(DBConfException, self).__init__(message)
		self.config = config
