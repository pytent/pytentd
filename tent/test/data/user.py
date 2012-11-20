'''
 Test cases for the user profile data

'''

from sqlalchemy.orm import sessionmaker

import unittest
import tent.data.dbm

from tent.data.user import User

class UserDataTest(unittest.TestCase):
    '''This test case verifies the functionality of the users data objects
    '''

    @classmethod
    def setUpClass(self):
        '''Configure test database, open connections
        ''' 
        config = { 'driver' : 'sqlite', 'path' : ':memory:'}
        self.engine = tent.data.dbm.connect(config)
        tent.data.dbm.install_tables(self.engine)
        
        Session =  sessionmaker(bind=self.engine)
        self.session = Session()
        
    @classmethod
    def tearDownClass(self):
        '''Close database connections, discard resources
        '''

    @classmethod
    def test_create_user(self):
        
        u = User("James Ravenscroft")
        self.session.add(u)

        our_user = self.session.query(User).filter_by(name='James Ravenscroft').first() 
        
        return u is our_user



if __name__ == "__main__":
    unittest.main()

