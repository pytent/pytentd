import os

from tests import AppTestCase, main

from tentd import db
from tentd.models.entity import Entity

class EntityBlueprintTest (AppTestCase):
    def test_serve_entity(self):
        user = Entity(name="testuser")
        db.session.add(user)
        db.session.commit()
        resp = self.test_client.head("/testuser/")
        assert resp.headers['Link'] == "http://localhost/testuser/profile"

if __name__ == "__main__":
    main()
