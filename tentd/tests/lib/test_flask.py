"""Test our flask extensions"""

from unittest import TestCase
from random import random

from bson import ObjectId
from flask import json
from mongoengine.queryset import QuerySet
from tentd.lib.flask import cached_method, Request, Blueprint, JSONEncoder

from tentd.utils.exceptions import APIBadRequest

class TestFlaskAdditions(TestCase):
    @cached_method
    def random(self):
        return random()
    
    def test_cached_method(self):
        return_value = self.random()
        assert return_value == self.random()

    def test_request_json(self):
        data = '{"key": "value"}'
        request = Request({'headers': {'mimetype': 'application/json'}})
        request.data = data
        assert request.json == json.loads(data)

    def test_request_invalid_json(self):
        request = Request({'headers': {'mimetype': 'application/json'}})
        request.data = 'this is not json'
        with self.assertRaises(APIBadRequest):
            request.json

    def test_Blueprint_get_endpoint_name(self):
        class TestView(object): pass
        assert Blueprint._get_endpoint_name(TestView) == 'test'

class TestJSONEncoder(TestCase):
    def json(self, obj):
        return json.dumps(obj, cls=JSONEncoder)

    def test_list(self):
        """Test that JSONEncoder handles lists"""
        assert self.json(['a', 'b', 'c'])
        
    def test_methods(self):
        """Test that JSONEncoder handles to_json() and __json__() methods"""
        class JSONEncodable(object):
            def to_json(self): return {'attribute': 'value'}

        assert self.json(JSONEncodable()) == '{"attribute": "value"}'

        class JSONEncodable(object):
            def __json__(self): return {'attribute': 'value'}

        assert self.json(JSONEncodable()) == '{"attribute": "value"}'

    def test_objectid(self):
        """Test that JSONEncoder handles ObjectIds"""
        objectid = ObjectId()
        assert self.json(objectid) == '"{}"'.format(objectid)
