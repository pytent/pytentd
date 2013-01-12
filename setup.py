#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name             = 'tentd',
    version          = '0.0.0',
    license          = 'Apache Software License 2.0',
    url              = 'https://github.com/ravenscroftj/pytentd',
    description      = 'A http://tent.io/ server and application',
    long_description = open('README.rst').read(),

    classifiers      = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: No Input/Output (Daemon)',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
    ],

    # Package
    
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': [
            'tentd = tentd.cli:run',
            'pytentd = tentd.cli:run',
        ]
    },

    # Requirements

    install_requires = [
        'flask==0.9',
        'Flask-MongoEngine',
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
