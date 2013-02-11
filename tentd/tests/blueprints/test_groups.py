"""Tests for the groups endpoint."""

from flask import json
from py.test import fixture, raises
from werkzeug.exceptions import NotFound

from tentd.documents import Group
from tentd.tests.http import GET, POST, PUT
from tentd.utils.exceptions import APIBadRequest

@fixture
def group(request, entity):
    group = Group(name="Test Group", entity=entity)
    request.addfinalizer(group.delete)
    return group.save()

def test_get_group(group):
    assert GET('groups.group', name=group.name).json() == group.to_json()

def test_get_missing_group(group):
    with raises(NotFound):
        GET('groups.group', name="Not a real group")
    
def test_get_groups(group):
    assert GET('groups.groups').json() == [group.to_json()]

def test_get_groups_empty(entity):
    assert GET('groups.groups').json() == []

def test_create_group(entity):
    POST('groups.groups', {'name': "Another Test Group"})
    assert entity.groups.get(name="Another Test Group")

def test_create_group(entity):
    with raises(APIBadRequest):
        POST('groups.groups', '<invalid>')

def test_update_group(entity, group):
    PUT('groups.group', {'name': "A renamed Test Group"}, name=group.name)
    with raises(Group.DoesNotExist):
        entity.groups.get(name="Test Group")
    assert entity.groups.get(name="A renamed Test Group")

def test_update_missing_group(group):
    with raises(APIBadRequest):
        PUT('groups.group', '<invalid>', name=group.name)

def test_delete_group(group):
    DELETE('groups.group', name=group.name)
    with raises(Group.DoesNotExist):
        entity.groups.get(name=group.name)

def test_delete_missing_group(entity):
    with raises(APIBadRequest):
        DELETE('groups.group', name='Not a real group')
