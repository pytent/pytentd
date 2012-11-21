'''
Main database module constructor/initial code

@author James Ravenscroft
@date  20/11/2012

'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr

Base = declarative_base()

#----------------------------------------------------------------------------

class TableMixin:
    '''Mixin class used as a base by all tent data objects.
    '''
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower() + 's'

#-----------------------------------------------------------------------------

class DBConfigurationException(Exception):
    
    '''Simple exception class used if the user db configuration doesn't work
    '''    
    
    def __init__(self, message, config):
        self.config = config
        Exception.__init__(message)

#-----------------------------------------------------------------------------

def connect( config ):
    
    '''This function is called to set up a database engine.

    This function is generally called once on import and sets up a database
    engine for use with ORM and such.

    '''
    
    if(config['driver'] == "sqlite"):
        connection_string = "sqlite:///%s" % config['path']
    else:
        raise DBConfigurationException("Invalid database configuration",
            config)

    engine = create_engine(connection_string,echo=True)
    return engine

#-------------------------------------------------------------------------------

def open_session( engine ):
    '''Set up an ORM session based upon an existing database engine
    '''
    Session =  sessionmaker(bind=engine)
    return Session() 

#-------------------------------------------------------------------------------

def install_tables( dbengine ):
    ''' Run a set of create queries on the given dbengine object
    '''
    Base.metadata.create_all(dbengine)
