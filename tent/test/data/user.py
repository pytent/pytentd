'''
 Test cases for the user profile data

'''

from sqlalchemy.orm import sessionmaker

import unittest
import tent.data.dbm
import tent.data.user

class UserDataTest(unittest.TestCase):
    '''This test case verifies the functionality of the users data objects
    '''

    def setUpClass(self):
        '''Configure test database, open connections
        ''' 
        config = { 'driver' : 'sqlite', 'path' : ':memory:'}
        self.engine = tent.data.dbm.connect(config)
        tent.data.dbm.install_tables()

        self.session = sessionmaker(bind=self.engine)
        
    def tearDownClass(self):
        '''Close database connections, discard resources
        '''

    def test_create_user(self):
        self.engine.



if __name__ == "__main__":
    unittest.main()

