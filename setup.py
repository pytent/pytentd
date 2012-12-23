#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name             = 'tentd',
    version          = '0.0.0',
    author           = 'James Ravenscroft',
    author_email     = 'ravenscroftj@gmail.com',
    url              = 'https://github.com/ravenscroftj/pytentd',
    description      = 'A http://tent.io/ server and application',
    long_description = open('README.rst').read(),

    # Package
    
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': ['tentd = tentd.cli:run']
    },

    # Requirements

    install_requires = [
        'flask==0.9',
        'Flask-SQLAlchemy==0.16',
        'requests==1.0.3',
        'simplejson==2.6.2'
    ],

    extras_require = {
        'daemon': ['daemonize==1.1']
    },

    # Tests
    
    test_suite = "tentd.tests",
    tests_require = [
        'mock==1.0.1',
    ],
)
