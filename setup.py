from setuptools import setup, find_packages

setup(
    name             = 'tentd',
    version          = '0.0.0',
    author           = 'James Ravenscroft',
    url              = 'https://github.com/ravenscroftj/pytentd',
    description      = 'A http://tent.io/ server and application',
    long_description = open('README.rst').read(),

    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,

    install_requires = [
        'flask==0.9',
        'Flask-SQLAlchemy==0.16'
    ],

    extras_require = {
        'daemon': ['daemonize==1.1']
    },

    entry_points = {
        'console_scripts': ['tentd = tentd:run']
    },
)
