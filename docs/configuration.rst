Configuration
=============

pytentd can load a configuration file into the Flask application, using the ``--conf [filename]`` command line option. This file should be a python file containing capitalised variables.

- ``SINGLE_USER_MODE``: Single user mode allows pytentd to skip the entity name section of the url in order to only provide for a single entity. This should be set to the name of a entity in the db to use, or None to run the server in multi-user mode (which is the default).
- ``USE_SUBDOMAINS``: Use entity names as subdomains (i.e. ``myname.example.com`` instead of ``example.com/myname/``). This conflicts with single user mode.
- ``THREADED``: Threaded mode is on by default, and is needed so that flask can fetch urls that it provides. It is not needed for single user mode and is only used when running tentd from the command line.

Documentation is also available on the configuration variables for `Flask`_ and `Flask-MongoEngine`_.

.. _Flask: http://flask.pocoo.org/docs/config/#builtin-configuration-values
.. _Flask-MongoEngine: https://flask-mongoengine.readthedocs.org/en/latest/

Example configuration file
--------------------------

::
    
    ## Use a collection named tentd on the mongodb server
    MONGODB_DB = 'tentd'

    ## The mongodb server location
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017

    ## Usernamed and password for the mongodb server
    MONGODB_USERNAME = 'example_username'
    MONGODB_PASSWORD = 'example_password'

    ## Threaded mode is needed so that flask can fetch urls that it provides.
    ## It is not needed for single user mode and is only used when running
    ## tentd from the command line.
    THREADED = False

    ## The name of the entity being used in single user mode
    ## This should be set to None or False to explicitly disable single user mode
    SINGLE_USER_MODE = 'name'
