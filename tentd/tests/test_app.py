"""Test the pytentd application"""

from flask import current_app
from py.test import mark, raises
from werkzeug.exceptions import ImATeapot

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

def test_coffee(app):
    """Test that /coffee raises an exception"""
    with raises(ImATeapot):
        assert GET('coffee')
