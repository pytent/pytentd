from json import loads, dumps

from flask import url_for

from tentd import db
from tentd.models.entity import Entity, Follower
from tentd.tests import TentdTestCase, patch, skip, MockFunction, MockResponse

import requests

class EntityBlueprintTest(TentdTestCase):
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
        
class FollowerTests(TentdTestCase):
    """
    TODO: Test connection errors
    """
    
    def before(self):
        self.user = Entity(name='localuser')
        self.commit(self.user)

        # Urls used for the follower entity
        self.identity     = 'http://follower.example.com'
        self.new_identity = 'http://changed.follower.example.com'
        self.profile      = 'http://follower.example.com/tentd/profile'
        self.notification = 'http://follower.example.com/tentd/notification'

        # Mocks for the server responses
        self.head = patch('requests.head', new_callable=MockFunction)
        self.head.start()

        profile_response = MockResponse(
            headers={'Link':
                '<{}>; rel="https://tent.io/rels/profile"'\
                .format(self.profile)})
        
        requests.head[self.identity] = profile_response
        requests.head[self.new_identity] = profile_response

        self.get = patch('requests.get', new_callable=MockFunction)
        self.get.start()
        
        requests.get[self.profile] = MockResponse(
            json={
                "https://tent.io/types/info/core/v0.1.0": {
                    "entity": self.identity,
                    "servers": ["http://follower.example.com/tentd"],
                    "licences": [],
                    "tent_version": "0.2",
                }})
        requests.get[self.notification] = MockResponse()
        
        # Assert that the mocks are working correctly
        self.assertIsInstance(requests.head, MockFunction)
        self.assertIsInstance(requests.get, MockFunction)

    def after(self):
        self.head.stop()
        self.get.stop()

    @skip("Waiting for tentd.control.follow.notify_following to be fixed")
    def test_entity_follow(self):
        response = self.client.post(
            '/localuser/followers',
            data=dumps({
                'entity': self.identity,
                'licences': [],
                'types': 'all',
                'notification_path': 'notification'
            }))

        # Ensure the request was made sucessfully.
        self.assertIsNotNone(response)
        self.assertStatus(response, 200)

        # Ensure the follower was created in the DB.
        self.assertIsNotNone(Follower.query.get(response.json['id']))
        
    def test_entity_follow_error(self):
        response = self.client.post('/localuser/followers', data='<invalid>')
        self.assertJSONError(response)

    def test_entity_follow_delete(self):
        # Add a follower to delete
        follower = Follower(
            identifier="http://tent.example.com/test",
            notification_path="notification")
        db.session.add(follower)
        db.session.commit()

        # Delete it.
        response = self.client.delete(
            '/localuser/followers/{}'.format(follower.id))
        self.assertEquals(200, response.status_code)

    def test_entity_follow_delete_non_existant(self):
        # TODO: This should use a JSON error, not a 404 code
        response = self.client.delete('/localuser/followers/0')
        self.assertEquals(404, response.status_code)

    @skip("This appears to not be updating the follower")
    def test_entity_follow_update(self):
        # Add a follower to delete
        follower = Follower(
            identifier='http://follower.example.com',
            notification_path='notification')
        self.commit(follower)

        response = self.client.put(
            '/localuser/followers/{}'.format(follower.id),
            data=dumps({'entity': self.new_identity}))
        
        # Ensure the request was made sucessfully.
        self.assertIsNotNone(response)
        self.assertStatus(response, 200)

        # Ensure the update happened sucessfully in the JSON.
        self.assertEquals(follower.id, response.json['id'])
        self.assertEquals(self.new_identity, response.json['identifier'])

        # Ensure the DB was updated
        updated_follower = Follower.query.get(follower.id)
        self.assertEquals(self.new_identity, updated_follower.identifier)
