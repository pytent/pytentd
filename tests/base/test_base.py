import os

from tests import AppTestCase, main

from flask import Flask, Config, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from tentd import create_app,db
from tentd.blueprints.base import base

from tentd.models.entity import Entity

from tempfile import mkstemp

class EntityServerTest( AppTestCase ):

    @classmethod
    def setUpClass(self):
        super(EntityServerTest, self).setUpClass()
        
        self.db_fd, self.dbname = mkstemp()

        config = Config(os.getcwd())
        config['DEBUG'] = True
        config['TESTING'] = True
        config['SQLALCHEMY_ECHO'] = True
        config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///%s" % self.dbname
        self.app = create_app(config)
        self.test_client = self.app.test_client()
        db.create_all(app=self.app)

    
    
    def test_serve_entity(self):

        #create an entity in the database
        username = "testuser"
        
        user1 = Entity(url=username)
        db.session.add(user1)
        db.session.commit()

        #get the response from the server
        resp = self.test_client.head("/%s" % username)

        assert resp.headers['Link'] == "http://localhost/testuser/profile"


    @classmethod
    def tearDownClass(self):
        os.close(self.db_fd) 
        os.unlink(self.dbname)

if __name__ == "__main__":
    main()
