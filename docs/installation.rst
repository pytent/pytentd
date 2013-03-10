Installing and running pytentd
==============================

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

Running pytentd
---------------

Running pytentd is easy::

    $ tentd

Information on the command line options can be found with::

    $ tentd --help

.. note::
   These instructions are currently incomplete. If you'd like to see instructions for another server, submit a pull request or issue on our github repository.

Gunicorn
^^^^^^^^

To run pytentd with gunicorn::

    $ gunicorn "tentd:create_app()"

Alternatively::

    $ gunicorn "tentd:create_app({'CONFIG_OPTION': 'value')"
    $ gunicorn "tentd:create_app('./path_to_config_file')"

Apache
^^^^^^

Pytentd can be run under Apache using `these instructions`_ and a `wsgi`_ file with the following contents::

    from tentd import create_app

    application = create_app()

In both the last two examples, the ``create_app`` function can take either the name of a configuration file (for an example see ``./tentd.conf.example``) or a dictionary of configuration values.

.. _these instructions: http://flask.pocoo.org/docs/deploying/mod_wsgi/
.. _wsgi: http://wsgi.readthedocs.org/en/latest/

Other servers
^^^^^^^^^^^^^

The Flask documentation also has instructions for running an application on other servers: `Deploying on Other Servers <http://flask.pocoo.org/docs/deploying/others/>`_.
