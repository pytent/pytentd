"""Tests for the groups endpoint."""

from tentd.documents import Group
from tentd.tests import EntityTentdTestCase

class GroupBlueprintTest(EntityTentdTestCase):
    """Tests for the groups endpoint."""
    def before(self):
        self.group = Group(group_name='Test', entity = self.entity).save()

    def test_get_groups(self):
        """Test that groups can be gotten."""
        r = self.client.get('/{}/groups', self.name)
        
        self.assertStatus(r, 200)
        self.assertEquals(r.json['name'], self.group.group_name)
