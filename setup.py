#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name             = 'tentd',
    version          = '0.1.1',
    license          = 'Apache Software License 2.0',
    url              = 'https://github.com/pytent/pytentd',

    maintainer       = 'James Ravencroft',
    maintainer_email = 'ravenscroftj@gmail.com',

    description      = 'A tent.io server',
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

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'tentd = tentd:run',
            'pytentd = tentd:run',
        ]
    },

    # Requirements

    install_requires=[
        'flask==0.9',
        'flask-mongoengine==0.6',
        'mongoengine==0.7.9',
        'blinker==1.1',
        'requests==1.1.0',
        'simplejson==3.0.7',
        'rfc3987==1.3.1'
    ],

    # Tests

    test_suite="tentd.tests",
    tests_require=[
        'mock==1.0.1',
    ],
)
