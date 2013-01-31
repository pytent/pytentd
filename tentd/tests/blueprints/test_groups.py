"""Tests for the groups endpoint."""

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

