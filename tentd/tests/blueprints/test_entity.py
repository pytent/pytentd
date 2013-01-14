"""Tests for the entity blueprint"""

from json import loads, dumps

import requests
from flask import url_for

from tentd import db
from tentd.documents.entity import Entity, Follower

from tentd.tests import TentdTestCase, EntityTentdTestCase, skip
from tentd.tests.mocking import MockFunction, MockResponse, patch

class EntityBlueprintTest(EntityTentdTestCase):
    def test_entity_link(self):
        self.assertEquals(
            self.client.head('/' + self.name).headers['Link'],
            '<{}{}/profile>; rel="https://tent.io/rels/profile"'.format(
                self.base_url, self.name))
    
    def test_entity_link_404(self):
        self.assertStatus(self.client.head('/non-existent-user'), 404)
    
    def test_entity_profile_404(self):
        self.assertStatus(
            self.client.head('/non-existent-user/profile'), 404)
    
    def test_entity_profile_json(self):
        """Test that /profile returns json"""
        r = self.client.get('/testuser/profile')
        
        self.assertEquals(r.mimetype, 'application/json')
        self.assertIn('https://tent.io/types/info/core/v0.1.0', r.json())
        
    def test_entity_core_profile(self):
        """Test that the core profile is returned correctly"""
        print url_for('entity.profile', entity=self.entity.name)
        
        r = self.client.get('/testuser/profile')
        url = r.json()['https://tent.io/types/info/core/v0.1.0']['entity']

        entity = Entity.objects.get(name=self.name)
        
        self.assertEquals(url, entity.core.identity)
        
class FollowerTests(EntityTentdTestCase):
    name = "localuser"
    
    @classmethod
    def beforeClass(self):
        # Urls used for the follower
        self.identity     = 'http://follower.example.com'
        self.profile      = 'http://follower.example.com/tentd/profile'
        self.notification = 'http://follower.example.com/tentd/notification'

        # Urls used to update the follower
        self.new_identity = 'http://changed.follower.example.com'
        self.new_profile  = 'http://follower.example.com/new/profile'
    
        # Mocks for the server responses
        self.head = patch('requests.head', new_callable=MockFunction)
        self.head.start()

        profile_response = MockResponse(
            headers={'Link':
                '<{}>; rel="https://tent.io/rels/profile"'\
                .format(self.profile)})

        new_profile_response = MockResponse(
            headers={'Link':
                '<{}>; rel="https://tent.io/rels/profile"'\
                .format(self.new_profile)})
        
        requests.head[self.identity] = profile_response
        requests.head[self.new_identity] = new_profile_response

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

        requests.get[self.new_profile] = MockResponse(
            json={
                "https://tent.io/types/info/core/v0.1.0": {
                    "entity": self.new_identity,
                    "servers": ["http://follower.example.com/tentd"],
                    "licences": [],
                    "tent_version": "0.2",
                }})

        requests.get[self.notification] = MockResponse()

    @classmethod
    def afterClass(self):
        self.head.stop()
        self.get.stop()

    def before(self):
        """Assert that the mocks are working correctly"""
        self.assertIsInstance(requests.head, MockFunction)
        self.assertIsInstance(requests.get, MockFunction)

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
        self.assertStatus(response, 200)

        # Ensure the follower was created in the DB.
        Follower.objects.get(id=response.json()['id'])
        
    def test_entity_follow_error(self):
        response = self.client.post('/localuser/followers', data='<invalid>')
        self.assertJSONError(response)

    def test_entity_follow_delete(self):
        # Add a follower to delete
        follower = Follower(
            entity=self.entity,
            identity="http://tent.example.com/test",
            notification_path="notification").save()

        # Delete it.
        response = self.client.delete(
            '/localuser/followers/{}'.format(follower.id))
        self.assertEquals(200, response.status_code)

    def test_entity_follow_delete_non_existant(self):
        # TODO: This should use a JSON error, not a 404 code
        response = self.client.delete('/localuser/followers/0')
        self.assertEquals(400, response.status_code)

    def test_entity_follow_update(self):
        # Add a follower to delete
        follower = Follower(
            entity=self.entity,
            identity='http://follower.example.com',
            notification_path='notification').save()

        response = self.client.put(
            '/localuser/followers/{}'.format(follower.id),
            data=dumps({'entity': self.new_identity}))
        
        # Ensure the request was made sucessfully.
        self.assertIsNotNone(response)
        self.assertStatus(response, 200)

        # Ensure the update happened sucessfully in the JSON.
        self.assertEquals(str(follower.id), response.json()['id'])
        self.assertEquals(self.new_identity, response.json()['identity'])

        # Ensure the DB was updated
        updated_follower = Follower.objects.get(id=follower.id)
        self.assertEquals(self.new_identity, updated_follower.identity)
