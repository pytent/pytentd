#!/usr/bin/env python

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    """Test runner for py.test"""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tentd/tests', '--mode=all']
        self.test_suite = True
    
    def run_tests(self):
        from pytest import main
        sys.exit(main(self.test_args))

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

    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
