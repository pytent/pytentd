from json import loads, dumps
from unittest import skip

from tests import AppTestCase, main

from flask import url_for

from tentd import db
from tentd.models.entity import Entity

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
        server = multiprocessing.Process(target=self.start_mock)
        server.start()

        import time
        time.sleep(5)

        r = self.client.post('/testuser/followers', data=dumps({
            'entity': self.external_base_url + 'testuser',
            'licences': [],
            'types': 'all',
            'notification_path': 'notification'}))

        server.terminate()
        server.join()
        print r.data
        self.assertEquals(200, r.status_code)

    def start_mock(self):
        self.external_app.run()

    def test_entity_follow_error(self):
        response = self.client.post('/testuser/followers', data='<invalid>')
        self.assertJSONError(response)
