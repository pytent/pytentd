"""Tests for the entity blueprint"""

from json import dumps

import requests

from tentd.documents.entity import Entity, Follower, Post
from tentd.documents.profiles import CoreProfile, BasicProfile

from tentd.tests import EntityTentdTestCase, skip
from tentd.tests.mocking import MockFunction, MockResponse, patch

class EntityBlueprintTest(EntityTentdTestCase):
    def test_entity_link(self):
        """Test that the link endpoint uses the correct header."""
        self.assertEntityHeader('/{}'.format(self.name))
    
    def test_entity_link_404(self):
        """Test that endpoints using an invalid user return 404."""
        self.assertStatus(self.client.head('/non-existent-user'), 404)

class ProfileBlueprintTest(EntityTentdTestCase):
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

    def test_entity_update_non_existant_profile(self):
        """Tests that attempting to update a non-existant profile fails."""
        update_data = {
            'servers': [
                'http://tent.example.com',
                'http://example.com/tent']}
        resp = self.client.put(
            '{}/profile/<invalid>'.format(self.name),
            data=dumps(update_data))
        self.assertStatus(resp, 404)

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

    def test_entity_link_follower(self):
        """Test that /{entity}/follower uses the tent header"""
        self.assertEntityHeader('/{}/followers'.format(self.name))

    def test_entity_follow(self):
        """Test that you can start following an entity."""
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
        response = self.client.delete(
            '/{}/followers/{}'.format(self.name, follower.id))
        self.assertEquals(200, response.status_code)

    def test_entity_follow_delete_non_existant(self):
        """Test that trying to stop following a non-existent user fails."""
        # TODO: This should use a JSON error, not a 404 code
        response = self.client.delete('/{}/followers/0'.format(self.name))
        self.assertEquals(400, response.status_code)

    def test_entity_follow_update(self):
        """Test that the following relationship can be edited correctly."""

        # Add a follower to update
        follower = Follower(
            entity=self.entity,
            identity='http://follower.example.com',
            notification_path='notification').save()

        response = self.client.put(
            '/{}/followers/{}'.format(self.name, follower.id),
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

class PostTests(EntityTentdTestCase):
    """Tests relating to the post routes."""
    
    def before(self):
        """Create a post in the DB."""
        self.new_post = Post()
        self.new_post.schema='https://tent.io/types/post/status/v0.1.0'
        self.new_post.content = {'text': 'test', 'location': None}
        self.new_post.entity = self.entity
        self.new_post.save()

    def test_entity_header_posts(self):
        """Test the entity header is returned from the posts route."""
        self.assertEntityHeader('/{}/posts'.format(self.name))

    def test_entity_get_posts(self):
        """Test that getting all posts returns correctly."""
        resp = self.client.get('/{}/posts'.format(self.name))
        self.assertStatus(resp, 200)

        posts = [post.to_json() for post in self.entity.posts]
        self.assertEquals(resp.json(), {'posts': posts})

    def test_entity_new_post(self):
        """Test that a new post can be added correctly."""
        post_details = {
            'schema': 'https://tent.io/types/post/status/v0.1.0', 
            'content': {'text': 'test', 'location': None}}
            
        resp = self.client.post('/{}/posts'.format(self.name),
            data=dumps(post_details))

        self.assertStatus(resp, 200)

        created_post = self.entity.posts.get(id=resp.json()['id'])
        self.assertIsNotNone(created_post)
        self.assertEquals(created_post.schema, post_details['schema'])
        self.assertEquals(created_post.content, post_details['content'])

    def test_entity_create_invalid_post(self):
        """Test that attempting to create an invalid post fails."""
        resp = self.client.post(
            '/{}/posts'.format(self.name), data='<invalid>')
        self.assertJSONError(resp)

    def test_entity_get_single_post(self):
        """Test getting a single post works correctly."""
        resp = self.client.get(
            '/{}/posts/{}'.format(self.name, self.new_post.id))

        self.assertStatus(resp, 200)
        self.assertEquals(resp.json(), self.new_post.to_json())

    def test_entity_update_single_post(self):
        """Test a single post can be updated."""
        resp = self.client.put(
            '/{}/posts/{}'.format(self.name, self.new_post.id),
            data=dumps({
                'content': {
                    'text': 'updated',
                    'location': None}}))

        new_post = Post.objects.get(entity=self.entity)
        self.assertStatus(resp, 200)
        self.assertEquals(resp.json(), new_post.to_json())

    def test_entity_update_post_invalid(self):
        """Test that attempting to update an invalid post fails."""
        resp = self.client.put(
            '/{}/posts/{}'.format(self.name, self.new_post.id),
            data='<invalid>')
        self.assertJSONError(resp)

    def test_entity_update_non_existant_post(self):
        """Test that attempting to update a non-existant post fails."""
        resp = self.client.put('/{}/posts/invalid'.format(self.name))
        self.assertStatus(resp, 404)

    def test_entity_delete_post(self):
        """Test that a post can be deleted."""
        resp = self.client.delete(
            '/{}/posts/{}'.format(self.name, self.new_post.id))
        self.assertStatus(resp, 200)
        entity_post = self.entity.posts.filter(id=self.new_post.id)
        self.assertEquals(entity_post.count(), 0)

    def test_entity_delete_invalid_post(self):
        """Test that attempting to delete a non-existant post fails."""
        resp = self.client.delete('/{}/posts/<invalid>'.format(self.name))
        self.assertStatus(resp, 404)

class MorePostTests(EntityTentdTestCase):
    def test_entity_get_empty_posts(self):
        """Test that /posts works when there are no posts to return"""
        resp = self.client.get('/{}/posts'.format(self.name))
        self.assertStatus(resp, 200)
        self.assertEquals(resp.json(), {})

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
