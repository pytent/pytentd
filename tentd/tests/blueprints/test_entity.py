"""Tests for the entity blueprint"""

from json import dumps

import requests

from tentd.documents.entity import Entity, Follower
from tentd.documents.profiles import CoreProfile, BasicProfile

from tentd.tests import TentdTestCase, EntityTentdTestCase, skip
from tentd.tests.mocking import MockFunction, MockResponse, patch

class EntityBlueprintTest(TentdTestCase):
    """Base tests for the entity blueprint."""
    def test_404(self):
        """Tests that non-existent users 404."""
        self.assertStatus(self.client.get("/non-existent-user"), 404)
        self.assertStatus(self.client.get("/non-existent-user/profile"), 404)
    
class ProfileBlueprintTest(EntityTentdTestCase):
    """Tests relating to profiles."""
    CORE = 'https://tent.io/types/info/core/v0.1.0'
    BASIC = 'https://tent.io/types/info/basic/v0.1.0'

    def test_entity_profile_404(self):
        """Test the the profile of a non-existent user returns 404."""
        self.assertStatus(self.client.head('/non-existent-user/profile'), 404)
   
    def test_entity_profile_link(self):
        """Test that the entity header on the entity profile is correct."""
        self.assertEntityHeader('/{}/profile'.format(self.name))
 
    def test_entity_profile_json(self):
        """Test that /profile returns json with a core profile"""
        r = self.client.get('/{}/profile'.format(self.name))
        
        self.assertEquals(r.mimetype, 'application/json')
        self.assertIn(CoreProfile.__schema__, r.json())
        
    def test_entity_core_profile(self):
        """Test that the core profile is returned correctly"""
        r = self.client.get('/{}/profile'.format(self.name))
        identity = r.json()[CoreProfile.__schema__]['entity']
        entity = Entity.objects.get(name=self.name)
        self.assertEquals(identity, entity.core.identity)

    def test_entity_get_single_profile(self):
        """Test that getting a single profile is possible."""
        resp = self.client.get('/{}/profile/{}'.format(
            self.name, CoreProfile.__schema__))
        self.assertStatus(resp, 200)

        core_profile = self.entity.profiles.get(CoreProfile.__schema__)
        self.assertEquals(resp.json(), core_profile.to_json())

    def test_entity_get_non_existant_profile(self):
        """Test that getting a non-existant profile fails."""
        resp = self.client.get('/{}/profile/<invalid>'.format(self.name))
        self.assertStatus(resp, 404)

    def test_entity_update_profile(self):
        """Tests that a profile can be updated."""
        update_data = {
            'servers': [
                'http://tent.example.com',
                'http://example.com/tent',]}

        resp = self.client.put(
            '{}/profile/{}'.format(self.name, CoreProfile.__schema__),
            data=dumps(update_data))

        servers = self.entity.profiles.get(CoreProfile.__schema__).servers

        self.assertStatus(resp, 200)
        self.assertEquals(servers, update_data['servers'])

    def test_entity_update_create_new_profile(self):
        """Tests that a new profile is created."""
        schema = 'https://testprofile.example.com/' 
        update_data = {
            'data': 'test'}
        resp = self.client.put(
            '{}/profile/{}'.format(self.name, schema),
            data=dumps(update_data))
        self.assertStatus(resp, 200)
        profile = self.entity.profiles.get(schema=schema)

        self.assertEquals(profile.to_json()['data'], update_data['data'])
        self.assertEquals(profile.schema, schema)

    @skip("ValidationErrors need some form of handling")
    def test_entity_update_unknown_profile(self):
        """Test that updating an unknown profile type fails."""
        resp = self.client.put('{}/profile/<invalid>'.format(self.name), 
            data = dumps({}))
        self.assertStatus(resp, 400)
        self.assertIn(
            "Invalid profile type '<invalid>'.", resp.json()['error'])

    def test_entity_invalid_update_profile(self):
        """Tests that updating a profile with invalid data fails."""
        resp = self.client.put('{}/profile/{}'.format(
            self.name, CoreProfile.__schema__))
        self.assertJSONError(resp)

    def test_entity_delete_profile(self):
        """Tests that a profile can be deleted."""
        new_profile = BasicProfile(entity=self.entity)
        new_profile.avatar_url = 'http://example.com/avatar.jpg'
        new_profile.name = 'test'
        new_profile.location = 'test'
        new_profile.gender = 'test'
        new_profile.birthdate = '01/01/1980'
        new_profile.bio = 'test'
        new_profile.save()

        # Will raise BasicProfile.DoesNotExist upon failing
        self.entity.profiles.get(schema=BasicProfile.__schema__)

        resp = self.client.delete(
            '{}/profile/{}'.format(self.name, BasicProfile.__schema__))
        self.assertStatus(resp, 200)

        profiles = self.entity.profiles.filter(schema=BasicProfile.__schema__)
        self.assertEquals(profiles.count(), 0)

    def test_entity_cannot_delete_core_profile(self):
        """Tests that the core profile cannot be deleted."""
        resp = self.client.delete(
            '{}/profile/{}'.format(self.name, CoreProfile.__schema__))
        self.assertStatus(resp, 400)

    def test_entity_delete_non_existent_profile(self):
        """Tests attempting to delete a non-existent profile fails."""
        resp = self.client.delete('{}/profile/<invalid>'.format(self.name))
        self.assertStatus(resp, 404)
        
class NotificationTest(EntityTentdTestCase):
    """Test routes relating to notifications."""

    @classmethod
    def beforeClass(cls):
        cls.identity = 'http://follower.example.com/tentd'
        cls.profile = 'http://follower.example.com/tentd/profile'
        cls.notification = 'http://follower.example.com/tentd/notification'

        cls.head = patch('requests.head', new_callable=MockFunction)
        cls.head.start()
        requests.head[cls.identity] = MockResponse(
            headers={'Link':
                '<{}>; rel="https://tent.io/rels/profile"'\
                .format(cls.profile)})

        cls.get = patch('requests.get', new_callable=MockFunction)
        cls.get.start()
        requests.get[cls.profile] = MockResponse(
            json={
                "https://tent.io/types/info/core/v0.1.0": {
                    "entity": cls.identity,
                    "servers": ["http://follower.example.com/tentd"],
                    "licences": [],
                    "tent_version": "0.2",
                }})

        cls.post = patch('requests.post', new_callable=MockFunction)
        cls.post.start()
        requests.post[cls.notification] = MockResponse()
        
    @classmethod
    def afterClass(cls):
        cls.head.stop()
        cls.get.stop()
        cls.post.stop()

    def before(self):
        self.assertIsInstance(requests.post, MockFunction)
        self.assertIsInstance(requests.get, MockFunction)

        self.follower = Follower(
            entity=self.entity,
            identity='http://follower.example.com/tentd',
            notification_path = 'notification'
        ).save()

    def test_entity_header_notification(self):
        """Test the entity header is returned from the notifications route."""
        self.assertEntityHeader('/{}/notification'.format(self.name))

    def test_notified_of_new_post(self):
        """Test that a followers notification path has a post made to it."""
        post_details = {
            'schema': 'https://tent.io/types/post/status/v0.1.0', 
            'content': {'text': 'test', 'location': None}}
        
        resp = self.client.post(
            '/{}/posts'.format(self.name),
            data=dumps(post_details))

        # Even though we've checked this,
        # make sure the response was sucessful.
        self.assertStatus(resp, 200)
        requests.post.assert_called(self.notification)

    def test_notification_created(self):
        """Test that a notification is raised correctly."""
        post_details = {
            'id': '1',
            'schema': 'https://tent.io/types/post/status/v0.1.0', 
            'content': {'text': 'test', 'location': None}}

        self.assertEquals(self.entity.notifications.count(), 0)
        resp = self.client.post('/{}/notification'.format(self.name), 
            data=dumps(post_details))
        self.assertStatus(resp, 200)
        self.assertEquals(self.entity.notifications.count(), 1)
        #TODO test that the notification raised has the correct details.
