"""py.test conftest file"""

import logging

from flask import _request_ctx_stack
from py.test import fixture
from werkzeug import ImmutableDict

from tentd import create_app
from tentd.documents import collections, Entity

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger('testing')

def drop_collections():
    log.info("Dropping collections")
    for collection in collections:
        collection.drop_collection()

DEFAULT_APP_CONFIGURATION = ImmutableDict({
    'DEBUG': True,
    'TESTING': True,
    'TRAP_HTTP_EXCEPTIONS': True,
    'PRESERVE_CONTEXT_ON_EXCEPTION': False,
    'SERVER_NAME': 'tentd.example.com',
    'MONGODB_SETTINGS': {
        'db': 'tentd-testing',
    },
})

@fixture(scope="class", params=['single_user_mode', 'multi_user_mode'])
def app(request):
    """An instance of the Tentd app"""
    
    configuration = DEFAULT_APP_CONFIGURATION.copy()
    if request.param == 'single_user_mode':
        configuration['SINGLE_USER_MODE'] = "single_user_name"
    configuration.update(getattr(request.module, 'tentd_configuration', {}))

    app = create_app(configuration)
    app.client = app.test_client()

    # Setup a request and application context
    ctx = app.test_request_context()
    ctx.push()
    
    # Drop all collections when finished
    request.addfinalizer(drop_collections)
    request.addfinalizer(ctx.pop)

    log.info("Created tentd application")
    if app.single_user_mode:
        log.info("Running in single user mode")
    
    return app

@fixture
def entity(request, app):
    entity = Entity.new(
        name=app.single_user_mode or 'testuser',
        identity= "http://example.com",
        servers=["http://tent.example.com"])

    request.addfinalizer(drop_collections)
    
    return entity.save()
