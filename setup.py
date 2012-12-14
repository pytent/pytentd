from setuptools import setup, find_packages

setup(
	name             = 'tentd',
	version          = "0.0.0",

	author           = 'James Ravenscroft',
	url              = 'https://github.com/ravenscroftj/pytentd',

	description      = 'An implementation of the http://tent.io server protocol',
	long_description = open('README.rst').read(),

	packages         = find_packages(),
	install_requires = [
		'flask==0.9',
		'Flask-SQLAlchemy==0.16',
                'daemonize>=1.1'
	],

	entry_points = {
		'console_scripts': ['tentd = tentd:run'],
	},
	
	include_package_data = True,
	zip_safe         = False,
)
