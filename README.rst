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
    $ tentd [subcommand] --help

Configuration
-------------

pytentd can load a configuration file into the Flask application, using the ``--conf [filename]`` command line option. This file should be a python file containing capitalised variables.

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
