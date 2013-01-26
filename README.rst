=======
pytentd
=======

A Python `tent.io <http://tent.io/>`_ server.

Running pytentd
===============

Running pytentd is easy::

    $ tentd

Information on the command line options can be found with::

    $ tentd --help

To run pytentd with gunicorn::

    $ gunicorn "tentd:create_app()"

Pytentd can be run under Apache using these `instructions`_ and a `wsgi`_ file with the following contents::

    from tentd import create_app

    application = create_app()

In both the last two examples, the ``create_app`` function can take either the name of a configuration file (for an example see ``./tentd.conf.example``) or a dictionary of configuration values.

The Flask documentation also has instructions for running an application on other servers: `Deploying on Other Servers <http://flask.pocoo.org/docs/deploying/others/>`_.

.. _instructions: http://flask.pocoo.org/docs/deploying/mod_wsgi/
.. _wsgi: http://wsgi.readthedocs.org/en/latest/

Installation
------------

The pytentd package can be installed with pip::

    pip install git+git://github.com/ravenscroftj/pytentd.git

The pytentd package can be also installed directly from the git repository::

    git clone git+git://github.com/ravenscroftj/pytentd.git
    cd pytentd
    python setup.py install

Pytentd requires a `mongoDB`_ database - packages for this are available for most operating systems. More information on starting and stopping the mongoDB server can be found `here`_, though some distributions (such as Ubuntu) will run mongoDB as a service once the package is installed.

.. _mongoDB: http://www.mongodb.org/
.. _here: http://www.mongodb.org/display/DOCS/Starting+and+Stopping+Mongo

Configuration
-------------

pytentd can load a configuration file into the Flask application, using the ``--conf [filename]`` command line option. This file should be a python file containing capitalised variables.

- ``SINGLE_USER_MODE``: Single user mode allows pytentd to skip the entity name section of the url in order to only provide for a single entity. This should be set to the name of a entity in the db to use, or None to run the server in multi-user mode (which is the default).
- ``THREADED``: Threaded mode is on by default, and is needed so that flask can fetch urls that it provides. It is not needed for single user mode and is only used when running tentd from the command line.

Documentation is available on the configuration variables for `Flask`_ and `Flask-MongoEngine`_.

.. _Flask: http://flask.pocoo.org/docs/config/#builtin-configuration-values
.. _Flask-MongoEngine: https://flask-mongoengine.readthedocs.org/en/latest/

Contributing
============

Coding Style
------------

We use `Google's Python style guide <http://google-styleguide.googlecode.com/svn/trunk/pyguide.html>`_ with a couple changes:

- Imports of global objects are acceptable, with the ``from ... import ...`` style being preferred.
- ``String.format()`` should be used instead of the coercion operator (``%``).

You should also try to write tests for any new code, which helps to ensure bugs get picked up more quickly.

We currently hang around in #os on irc.aberwiki.org, feel free to join and come and chat to us :)

Running tests
-------------

To run the tests on the installed pytentd package::

    python -m unittest discover tentd

To run the tests on the pytentd source::

    cd pytentd
    python setup.py test

Other tools
-----------

`nose`_ and `sniffer`_ are both useful test runners. Nose alone makes running tests a little easier, and can run the tests both from the source or on an installed module.
Sniffer is a tool built on top of nose, and will run the tests each time the source is modified.

While developing, `pyflakes`_ and `pylint`_ are useful for checking code quality.

.. _nose: https://nose.readthedocs.org/en/latest/index.html
.. _sniffer: http://pypi.python.org/pypi/sniffer

.. _pyflakes: http://pypi.python.org/pypi/pyflakes
.. _pylint: http://pypi.python.org/pypi/pylint

License
=======

pytentd is licensed under the Apache License 2.0.
For details, see the LICENSE file.
