"""Tests for the entity blueprint"""

from json import dumps

from tentd.documents.entity import Post
from tentd.flask import jsonify
from tentd.tests import EntityTentdTestCase

class PostTests(EntityTentdTestCase):
    """Tests relating to the post routes."""
    
    def before(self):
        """Create a post in the DB."""
        self.new_post = Post.new(
            entity=self.entity,
            schema='https://tent.io/types/post/status/v0.1.0',
            content={'text': 'test', 'location': None}).save()

    def test_entity_header_posts(self):
        """Test the entity header is returned from the posts route."""
        self.assertEntityHeader('/{}/posts'.format(self.name))

    def test_entity_get_posts(self):
        """Test that getting all posts returns correctly."""
        resp = self.client.get('/{}/posts'.format(self.name))
        self.assertStatus(resp, 200)

        posts = [post.to_json() for post in self.entity.posts]
        self.assertEquals(resp.data, jsonify(posts).data)

    def test_entity_new_post(self):
        """Test that a new post can be added correctly."""
        details = {
            'schema': 'https://tent.io/types/post/status/v0.1.0', 
            'content': {'text': 'test', 'location': None}}
            
        resp = self.client.post('/{}/posts'.format(self.name),
            data=dumps(details))

        self.assertStatus(resp, 200)

        created_post = self.entity.posts.get(id=resp.json()['id'])
        self.assertIsNotNone(created_post)
        self.assertEquals(created_post.schema, details['schema'])
        self.assertEquals(created_post.latest.content, details['content'])

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
        self.assertEquals(resp.data, jsonify(self.new_post).data)

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
        self.assertEquals(resp.data, jsonify(new_post).data)

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

class VersionsTest(EntityTentdTestCase):
    def before(self):
        self.post = Post(
            entity=self.entity,
            schema='https://tent.io/types/post/status/v0.1.0')

        self.post.new_version(content={'text': "Hello world"})
        self.post.new_version(content={'text': "Goodbye world"})

        self.post.save()

    def test_get_post_version(self):
        """Test GET /posts/<id>/versions"""
        response = self.client.get(
            '/testuser/posts/{}/versions'.format(self.post.id))
        assert response.status_code == 200

        versions = [v.to_json() for v in self.post.versions][::-1]
        assert response.json() == versions

    def test_delete_post_version(self):
        """Test DELETE /posts/<id>?version=<num>"""

        # Delete the post version
        response = self.client.delete(
            '/testuser/posts/{}?version=0'.format(self.post.id))
        assert response.status_code == 200

        # Check the post version has been deleted
        post = self.entity.posts.get(id=self.post.id)
        assert len(post.versions) == 1

        # Delete the last version of the post, expecting an error
        self.assertJSONError(self.client.delete(
            '/testuser/posts/{}?version=0'.format(self.post.id)))

class MorePostsTest(EntityTentdTestCase):
    """Tests for posts without having existing posts."""
    def test_entity_get_empty_posts(self):
        """Test that /posts works when there are no posts to return"""
        resp = self.client.get('/{}/posts'.format(self.name))
        self.assertStatus(resp, 200)
        self.assertEquals(resp.json(), [])
