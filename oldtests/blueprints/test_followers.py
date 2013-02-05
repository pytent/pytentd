"""Tests for the entity blueprint"""

from json import dumps

import requests

from tentd.documents.entity import Follower

from tentd.tests import EntityTentdTestCase, MockFunction, MockResponse, patch

class FollowerTests(EntityTentdTestCase):
    """Tests relating to followers."""
    name = "localuser"
    
    @classmethod
    def beforeClass(self):
        """Set up details of followers."""
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
        
        requests.get[self.notification] = MockResponse()
        
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

    @classmethod
    def afterClass(self):
        """Clean up after testing."""
        self.head.stop()
        self.get.stop()

    def before(self):
        """Assert that the mocks are working correctly"""
        self.assertIsInstance(requests.head, MockFunction)
        self.assertIsInstance(requests.get, MockFunction)

    def test_entity_follow(self):
        """Test that you can start following an entity."""
        response = self.client.post(
            '/localuser/followers',
            data=dumps({
                'entity': self.identity,
                'licences': [],
                'types': 'all',
                'notification_path': 'notification'
            }), content_type='application/json')

        # Ensure the request was made sucessfully.
        self.assertStatus(response, 200)

        # Ensure the follower was created in the DB.
        Follower.objects.get(id=response.json()['id'])

        requests.get(self.notification)
        requests.get.assert_called(self.notification)
       
    def test_entity_follow_error(self):
        """Test that trying to follow an invalid entity will fail."""
        response = self.client.post(
            '/{}/followers'.format(self.name), data='<invalid>')
        self.assertJSONError(response)
        requests.get.assert_not_called(self.notification)

    def test_entity_follow_delete(self):
        """Test that an entity can stop being followed."""
        # Add a follower to delete
        follower = Follower(
            entity=self.entity,
            identity="http://tent.example.com/test",
            notification_path="notification").save()

        # Delete it.
        response = self.secure_client.delete(
            '/{}/followers/{}'.format(self.name, follower.id))
        self.assertEquals(200, response.status_code)

    def test_entity_follow_delete_non_existant(self):
        """Test that trying to stop following a non-existent user fails."""
        response = self.secure_client.delete('/{}/followers/0'.format(self.name))
        self.assertEquals(400, response.status_code)

    def test_entity_follow_update(self):
        """Test that the following relationship can be edited correctly."""

        # Add a follower to update
        follower = Follower(
            entity=self.entity,
            identity='http://follower.example.com',
            notification_path='notification').save()

        response = self.secure_client.put(
            '/{}/followers/{}'.format(self.name, follower.id),
            data=dumps({'entity': self.new_identity}),
            content_type='application/json')
        
        # Ensure the request was made sucessfully.
        self.assertIsNotNone(response)
        self.assertStatus(response, 200)

        # Ensure the update happened sucessfully in the JSON.
        self.assertEquals(str(follower.id), response.json()['id'])
        self.assertEquals(self.new_identity, response.json()['identity'])

        # Ensure the DB was updated
        updated_follower = Follower.objects.get(id=follower.id)
        self.assertEquals(self.new_identity, updated_follower.identity)
