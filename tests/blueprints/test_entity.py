from json import loads, dumps

from flask import url_for

from tentd import db
from tentd.models.entity import Entity, Follower

from tests import AppTestCase, skip

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

import mock
import requests

class MockFunction(dict):
    """A callable argument->value dictionary for patching over a function

    New argument->value pairs can be assigned in the same way as a dict,
    and values can be returned by calling it as a function.
    """
    
    def __call__(self, argument):
        """Return the value, setting it's __argument__ attribute"""
        if argument in self:
            self[argument].__argument__ = argument
            return self[argument]
        raise KeyError("No mock response set for '{}'".format(argument))

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            super(MockFunction, self).__repr__())

class MockResponse(mock.NonCallableMock):
    """A mock response, for use with MockFunction"""

    #: Use a default status code
    status_code = 200

    #: The argument the response is for
    __argument__ = None

    def __str__(self):
        return "<MockResponse for {}>".format(self.__argument__)

class FollowerTests(AppTestCase):
    """
    TODO: Test connection errors
    """
    
    def before(self):
        self.user = Entity(name='localuser')
        self.commit(self.user)

        # Urls used for the follower entity
        self.identity     = 'http://follower.example.com'
        self.profile      = 'http://follower.example.com/tentd/profile'
        self.notification = 'http://follower.example.com/tentd/notification'

        # Mocks for the server responses
        self.head = mock.patch('requests.head', new_callable=MockFunction)
        self.head.start()
        
        requests.head[self.identity] = MockResponse(
            headers={'Link': '<{}>; rel="https://tent.io/rels/profile"'.format(
                self.profile)})

        self.get = mock.patch('requests.get', new_callable=MockFunction)
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

    @skip("Requires mocks")
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

    @skip("Requires mocks")
    def test_entity_follow_update(self):
        # Add a follower to delete
        follower = Follower(
            identifier='http://follower.example.com',
            notification_path='notification')
        self.commit(follower)

        new_identifier = 'http://changed.follower.example.com'

        response = self.client.put(
            '/localuser/followers/{}'.format(follower.id),
            data=dumps({'entity': new_identifier}))
        
        # Ensure the request was made sucessfully.
        self.assertIsNotNone(response)
        self.assertStatus(response, 200)

        # Ensure the update happened sucessfully in the JSON.
        self.assertEquals(follower.id, r.json['id'])
        self.assertEquals(new_identifier, r.json['identifier'])

        # Ensure the DB was updated
        updated_follower = Follower.query.get(follower.id)
        self.assertEquals(new_identifier, updated_follower.identifier)
