Contributing to pytentd
=======================

The pytentd developers can usually be found in #os on `irc.aberwiki.org`, and #tent on `Freenode`_, feel free to come and chat to us, or ask any questions you may have.

.. _irc.aberwiki.org: irc://irc.aberwiki.org/
.. _Freenode: http://freenode.net/

Coding Style
------------

We use Google's `Python style guide`_, with some small changes:

- Imports should use the ``from ... import ...`` style.
- ``String.format()`` should be always be used instead of the coercion operator (``%``).

You should also try to write tests for any new code, which helps to ensure bugs get picked up more quickly.

.. _Python style guide: http://google-styleguide.googlecode.com/svn/trunk/pyguide.html

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
