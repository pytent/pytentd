"""Test our flask extensions"""

from random import random

from bson import ObjectId
from flask import json
from mongoengine.queryset import QuerySet
from tentd.lib.flask import (
    cached_method, Request, Blueprint, JSONEncoder, jsonify)

from tentd.utils.exceptions import APIBadRequest

class TestFlaskAdditions(object):
    @cached_method
    def cached_random_method(self):
        return random()
    
    def test_cached_method(self):
        assert self.cached_random_method() == self.cached_random_method()

    def test_Blueprint_get_endpoint_name(self):
        class TestView(object): pass
        assert Blueprint._get_endpoint_name(TestView) == 'test'

class JSONEncodable(object):
    def to_json(self):
        return {'attribute': 'value'}

class AlternateJSONEncodable(object):
    def __json__(self):
        return {'attribute': 'value'}

class TestJSONEncoder(object):
    def dumps(self, obj):
        return json.dumps(obj, cls=JSONEncoder)

    def test_list(self):
        """Test that JSONEncoder handles lists"""
        assert self.dumps(['a', 'b', 'c'])
        
    def test_methods(self):
        """Test that JSONEncoder handles to_json() and __json__() methods"""
        for cls in (JSONEncodable, AlternateJSONEncodable):
            assert self.dumps(cls()) == '{"attribute": "value"}'

    def test_objectid(self):
        """Test that JSONEncoder handles ObjectIds"""
        objectid = ObjectId()
        assert self.dumps(objectid) == '"{}"'.format(objectid)

def test_jsonify_types(app):
    """Test that jsonify works with all of our custom types"""
    with app.test_request_context():
        for cls in (list, dict, ObjectId, JSONEncodable):
            assert jsonify(cls())

def test_jsonify_mimetype(app):
    """Test that jsonify() uses the correct mimetype"""
    mimetypes = (
        'application/vnd.tent.v0+json',
        'application/json',
        'text/json')

    for mimetype in mimetypes:
        with app.test_request_context(content_type=mimetype):
            assert jsonify([]).mimetype == mimetype

def test_jsonify_default_mimetype(app):
    """Test that jsonify() uses the correct default mimetype"""
    with app.test_request_context():
        assert jsonify([]).mimetype == 'application/vnd.tent.v0+json'
