"""Tests for the groups endpoint."""

from json import dumps

from tentd.documents import Group
from tentd.tests import EntityTentdTestCase

class GroupBlueprintTest(EntityTentdTestCase):
    """Tests for the groups endpoint."""
    def before(self):
        self.group = Group(name='Test', entity = self.entity).save()

    def test_get_groups(self):
        """Test that groups can be gotten."""
        r = self.client.get('/{}/groups'.format(self.name))
        self.assertStatus(r, 200)
        self.assertIn(self.group.to_json(), r.json())

    def test_get_two_groups(self):
        """Test that two groups can be gotten."""
        group_two = Group(name="tentd", entity = self.entity).save()
        r = self.client.get('/{}/groups'.format(self.name))
        self.assertStatus(r, 200)
        self.assertIn(self.group.to_json(), r.json())
        self.assertIn(group_two.to_json(), r.json())

    def test_create_group(self):
        """Test that a group can be created."""
        group_data = {'name': 'tentd'}
        r = self.client.post('/{}/groups'.format(self.name), 
            data=dumps(group_data))
        self.assertStatus(r, 200)
        
        created_group = self.entity.groups.get(name=group_data['name'])
        self.assertIsNotNone(created_group)
        self.assertEquals(created_group.name, group_data['name'])

    def test_create_group_invalid_data(self):
        """Tests that creating a group with invalid data fails."""
        resp = self.client.post('/{}/groups'.format(self.name), 
                data = '<invalid>')
        self.assertJSONError(resp)

class MoreGroupBluePrintTest(EntityTentdTestCase):
    """Test for the groups endpoint without before processing."""
    def test_get_empty_groups(self):
       """Test that getting an entity with no groups returns an empty list"""
       r = self.client.get('/{}/groups'.format(self.name))
       self.assertStatus(r, 200)
       self.assertEquals(r.json(), [])
