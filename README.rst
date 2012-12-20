pytentd
=======

A Python `tent.io <http://tent.io/>`_ server and application.

Currently, only the server is being developed.

Running pytentd
---------------

Running pytentd is easy::

    $ tentd

Information on the command line options can be found with::

    $ tentd --help
    $ tentd daemon --help

Configuration
-------------

pytentd can load a configuration file into the Flask application.
This file should be a python file containing capitalised variables.

These configuration variables can be used for pytentd:

- ``PIDFILE``: The path used for the pidfile in daemon mode.

Documentation is also available on the configuration variables for `Flask`_ and `SQLAlchemy`_.

.. _Flask: http://flask.pocoo.org/docs/config/#builtin-configuration-values
.. _SQLAlchemy: http://packages.python.org/Flask-SQLAlchemy/config.html

Contributing
============

We use `Google's Python style guide <http://google-styleguide.googlecode.com/svn/trunk/pyguide.html>`_ with a couple changes:

- Imports of global objects are acceptable, with the `from ... import ...` style being preferred.
- `String.format()` should be used instead of the coercion operator (`%`).

You should also try to write tests for any new code, which helps to ensure bugs get picked up more quickly.

We currently hang around in #os on irc.aberwiki.org, feel free to join and come and chat to us :)

Running tests
-------------

The unittests can be run with `nose`_, run from the root of the repository.
Alternatively, `sniffer`_ will run the tests whenever the source is changed.

While developing, `tabnanny`_ and `pylint`_ are useful for checking code quality.

.. _nose: https://nose.readthedocs.org/en/latest/index.html
.. _sniffer: http://pypi.python.org/pypi/sniffer

.. _tabnanny: http://docs.python.org/2/library/tabnanny.html
.. _pylint: http://pypi.python.org/pypi/pylint
