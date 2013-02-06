"""py.test conftest file"""

import logging
from termcolor import colored

from flask import _request_ctx_stack
from py.test import fixture
from werkzeug import ImmutableDict

from tentd import create_app
from tentd.documents import collections, Entity

logging.basicConfig(level=logging.INFO)

log = logging.getLogger('testing')

def pytest_runtest_call(item):
    """Log each test"""
    log.info("Running {}".format(item.obj.__name__))

def drop_collections():
    """Function to drop all of the collections used by pytentd"""
    log.debug("Dropping collections")
    for collection in collections:
        collection.drop_collection()

    for collection in collections:
        assert collection.objects.count() == 0

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

MULTIPLE, SINGLE = 'Multiple user mode', 'Single user mode'

@fixture(scope="module", params=[MULTIPLE, SINGLE])
def app(request):
    """Create an instance of the Tentd app prepared for testing"""
    configuration = DEFAULT_APP_CONFIGURATION.copy()
    if request.param == SINGLE:
        configuration['SINGLE_USER_MODE'] = "single_user_name"

    app = create_app(configuration)
    app.client = app.test_client()

    # Setup a request and application context
    ctx = app.test_request_context()
    ctx.push()
    request.addfinalizer(ctx.pop)

    # Drop all collections when finished
    request.addfinalizer(drop_collections)

    log.info("Created pytentd application[{}]".format(request.param))

    return app

@fixture(scope="function")
def entity(request, app):
    entity = Entity.new(
        name=app.single_user_mode or 'testuser',
        identity= "http://example.com",
        servers=["http://tent.example.com"])

    request.addfinalizer(drop_collections)
    
    return entity.save()
