from json import loads, dumps
from unittest import skip

from tests import AppTestCase, main

from flask import url_for

from tentd import db
from tentd.models.entity import Entity, Follower

import multiprocessing

class EntityBlueprintTest(AppTestCase):
    def before(self):
        self.name = 'testuser'
        self.user = Entity(name=self.name)
        self.commit(self.user)

    def test_entity_link(self):
        self.assertEquals(
            self.client.head('/' + self.name).headers['Link'],
            '<{}{}/profile>; rel="https://tent.io/rels/profile"'.format(
                self.base_url, self.name))
    
    def test_entity_link_404(self):
        self.assertStatus(self.client.head('/non-existent-user'), 404)
    
    def test_entity_profile_404(self):
        self.assertStatus(self.client.head('/non-existent-user/profile'), 404)
    
    def test_entity_profile_json(self):
        r = self.client.get('/testuser/profile')
        
        self.assertEquals(r.mimetype, 'application/json')
        self.assertIn('https://tent.io/types/info/core/v0.1.0', r.json)
        
    def test_entity_core_profile(self):
        r = self.client.get('/testuser/profile')
        url = r.json['https://tent.io/types/info/core/v0.1.0']['entity']
        
        self.assertEquals(url, self.base_url + self.name)

#    @skip("This doesn't work yet")
    def test_entity_follow(self):
        try:
            # Start the external server.
            self.start_mocked_server()

            # Make the request.
            r = self.client.post('/testuser/followers', data=dumps({
                'entity': self.external_base_url + 'testuser',
                'licences': [],
                'types': 'all',
                'notification_path': 'notification'}))
        finally:
            # Clean up the external server.
            self.stop_mocked_server()

        # Ensure the request was made sucessfully.
        self.assertNotEquals(None, r)
        self.assertEquals(200, r.status_code)

        # Ensure the follower was created in the DB.
        self.assertNotEquals(None, r.json['id'])
        self.assertNotEquals(None, Follower.query.get(r.json['id']))

    def start_mocked_server(self):
        """ Start the mocked tentd server. """
        self.server = multiprocessing.Process(target=self.start_mock)
        self.server.start()

        import time
        time.sleep(5)

    # TODO is this actually needed?
    def start_mock(self):
        """ Wrap the call so it can actually be used. """
        self.external_app.run()

    def stop_mocked_server(self):
        """ Stop the mocked tentd server. """
        self.server.terminate()
        self.server.join()

    def test_entity_follow_error(self):
        response = self.client.post('/testuser/followers', data='<invalid>')
        self.assertJSONError(response)

    def test_entity_follow_delete(self):
        # Add a follower to delete
        follower = Follower(identifier="http://tent.example.com/test", notification_path="notification")
        db.session.add(follower)
        db.session.commit()

        # Delete it.
        response = self.client.delete('/testuser/followers/{}'.format(follower.id))
        self.assertEquals(200, response.status_code)

    def test_entity_follow_delete_non_existant(self):
        response = self.client.delete('/testuser/followers/0')
        self.assertEquals(404, response.status_code)

    def test_entity_follow_update(self):
        # Add a follower to delete
        follower = Follower(identifier="http://tent.example.com/test", notification_path="notification")
        db.session.add(follower)
        db.session.commit()

        try:
            self.start_mocked_server()
            r = self.client.put('/testuser/followers/{}'.format(follower.id), data=dumps({ 
                'entity': self.external_base_url + 'testuser'
            }))
        finally:
            self.stop_mocked_server()

        # Ensure the request was made sucessfully.
        self.assertNotEquals(None, r)
        self.assertEquals(200, r.status_code)

        print r.json

        # Ensure the update happened sucessfully in the JSON.
        self.assertEquals(follower.id, r.json['id'])
        self.assertEquals(self.external_base_url + 'testuser', r.json['identifier'])

        # Ensure the DB was updated too.
        updated_follower = Follower.query.get(follower.id)
        self.assertEquals(self.external_base_url + 'testuser', updated_follower.identifier)
