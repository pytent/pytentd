import os

from tests import AppTestCase, main

from tentd import db
from tentd.blueprints.base import base
from tentd.models.entity import Entity

class EntityServerTest (AppTestCase):
    def test_serve_entity(self):

        #create an entity in the database
        username = "testuser"
        
        user1 = Entity(url=username)
        db.session.add(user1)
        db.session.commit()

        #get the response from the server
        resp = self.test_client.head("/%s" % username)

        assert resp.headers['Link'] == "http://localhost/testuser/profile"

if __name__ == "__main__":
    main()
