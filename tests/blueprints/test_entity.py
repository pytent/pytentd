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

class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __get_attribute__(self, name):
        raise NotImplementedError("No attribute assigned to '{}'".format(name))

class MockResponse(Mock):
    #: Use a default status code
    status_code = 200

class MockResponses(dict):
    """A dictionary that can be used """
    def __call__(self, url):
        try:
            return self[url]
        except KeyError:
            raise KeyError("No mock response set for url '{}'".format(url))

from mock import patch, DEFAULT
import requests

class FollowerTests(AppTestCase):
    """
    TODO: Test connection errors
    """
    
    def before(self):
        self.user = Entity(name='localuser')
        self.commit(self.user)

    @patch.multiple(requests, head=DEFAULT, get=DEFAULT)
    def test_entity_follow(self, head, get):
        self.assertEquals(requests.head, head)
        self.assertEquals(requests.get, get)

        identity = 'http://follower.example.com'
        profile = 'http://follower.example.com/tentd/profile'
        notification = 'http://follower.example.com/tentd/notification'
        
        head.side_effect = MockResponses()
        head.side_effect[identity] = MockResponse(
            headers={'Link':
                '<{}>; rel="https://tent.io/rels/profile"'.format(profile)})

        get.side_effect = MockResponses()
        get.side_effect[profile] = MockResponse(
            json={
                "https://tent.io/types/info/core/v0.1.0": {
                    "licences": [],
                    "servers": ["http://follower.example.com/tentd"],
                    "tent_version": "0.2",
                    "entity": identity}})
        get.side_effect[notification] = MockResponse()

        
        response = self.client.post(
            '/localuser/followers',
            data=dumps({
                'entity': identity,
                'licences': [],
                'types': 'all',
                'notification_path': 'notification'
            }))

        # Ensure the request was made sucessfully.
        self.assertIsNotNone(response)
        self.assertStatus(response, 200)

        # Ensure the follower was created in the DB.
        self.assertIsNotNone(Follower.query.get(response.json['id']))
        
    @skip("")
    def test_entity_follow_error(self):
        response = self.client.post('/testuser/followers', data='<invalid>')
        self.assertJSONError(response)

    @skip("")
    def test_entity_follow_delete(self):
        # Add a follower to delete
        follower = Follower(identifier="http://tent.example.com/test", notification_path="notification")
        db.session.add(follower)
        db.session.commit()

        # Delete it.
        response = self.client.delete('/testuser/followers/{}'.format(follower.id))
        self.assertEquals(200, response.status_code)

    @skip("")
    def test_entity_follow_delete_non_existant(self):
        response = self.client.delete('/testuser/followers/0')
        self.assertEquals(404, response.status_code)

    @skip("")
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
