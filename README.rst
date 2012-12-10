=======
pytentd
=======

A Python implementation of the `tent.io <http://tent.io/>`_ server protocol and a client to go on top too.

Running pytentd
---------------

Running pytentd is easy: ``python -m tentd tentd.cfg``

Configuration
-------------

- Flask: http://flask.pocoo.org/docs/config/#builtin-configuration-values
- Database: http://packages.python.org/Flask-SQLAlchemy/config.html

Running tests
-------------

The unittests can be run with ``nosetests``, run from the root of the repository. 
Alternatively, ``sniffer` will run them whenever the files change.

There are also some other useful commands for checking code quality::
	
	# Check for mixed tabs and spaces
	python -m tabnanny -v tentd
	
	# Static source analysis
	pylint tentd
