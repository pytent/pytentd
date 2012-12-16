"""Default arguments for tentd"""

from os import getcwd

# Place the database in the current directory
SQLALCHEMY_DATABASE_URI = "sqlite:///{}/tentd.db".format(getcwd())

# The name of the pidfile used by the daemon mode
PIDFILE = "/var/run/pytentd.pid"
