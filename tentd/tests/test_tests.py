"""Test the HTTP functions in tentd.tests"""

from flask import current_app

from tentd.lib.flask import Response
from tentd.tests import HTTP, GET, PUT, POST, HEAD

def test_http_type():
    """Check that the HTTP methods have been built correctly"""
    for http in GET, PUT, POST, HEAD:
        assert isinstance(http, HTTP)

def test_http_get(app):
    """Test that the correct Response class is being used"""
    assert type(GET('home')) == current_app.response_class == Response

def test_http_json(app):
    """Test that the Response.json() method works"""
    assert 'version' in GET('home').json()
