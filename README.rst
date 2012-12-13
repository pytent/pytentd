=======
pytentd
=======

A Python implementation of the `tent.io <http://tent.io/>`_ server protocol and a client to go on top too.

Installing pytentd
------------------

Run: ``python setup.py build``
followed by: ``python setup.py install`` as an administrative user.

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
Alternatively, ``sniffer`` will run them whenever the files change.

There are also some other useful commands for checking code quality::
	
	# Check for mixed tabs and spaces
	python -m tabnanny -v tentd
	
	# Static source analysis
	pylint tentd

Advanced Configuration
----------------------

For more advance users who want a webserver to wrap pytentd in, you will need to proxy the through 
to flask. You may find that external URLs come through as http://localhost:5000, if so you need to
look at the proxy_pass flags: 
http://flask.pocoo.org/mailinglist/archive/2011/3/14/problem-with-apache-proxy-and-canonical-urls/#f2a36991baa8f41c6671b91ce8269f2a

Example nginx virtualhost:

``server {
        listen 80;
        server_name tentd.example.com;

        location / {
                proxy_pass http://localhost:5000/;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header Host $http_host;
        }
}``
