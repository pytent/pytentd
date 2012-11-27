from setuptools import setup, find_packages
from tentd import __version__, __doc__

setup(
    name             = 'tentd',
    version          = __version__,

    author           = 'James Ravenscroft',
    url              = 'https://github.com/ravenscroftj/pytentd',
    
    description      = __doc__,
    long_description = open('README.rst').read(),
    
    packages         = find_packages(),
    install_requires = ['flask==0.9'],
    
    include_package_data = True,
    zip_safe         = False,
)
