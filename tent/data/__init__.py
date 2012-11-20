'''
Main database module constructor/initial code

'''

from sqlalchemy import create_engine



class DBConfigurationException(Exception):
    
    '''Simple exception class used if the user db configuration doesn't work
    '''    
    
    def __init__(self, message, config):
        self.config = config
        Exception.__init__(message)


def init( config ):

    if(config['driver'] == "sqlite"):
        engine = create_engine('sqlite:///:memory:', echo=True)
