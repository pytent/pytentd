"""Default arguments for tentd"""

from os import getcwd

# Place the database in the current directory
MONGODB_SETTINGS = {
    'db': 'tentd',
}

# The name of the pidfile used by the daemon mode
PIDFILE = "/var/run/pytentd.pid"
