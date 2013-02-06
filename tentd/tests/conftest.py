"""py.test conftest file"""

import logging

from flask import _request_ctx_stack
from py.test import fixture
from werkzeug import ImmutableDict

from tentd import create_app
from tentd.documents import collections, Entity

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('testing')

#: Constant values for single and multi user modes
MULTIPLE, SINGLE = 'multiple user mode', 'single user mode'

#: The configuration used to create instances of the tentd app
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

def pytest_addoption(parser):
    """Add an option to chose the modes tests will be run under"""
    parser.addoption("--mode", action="store", default="both",
        help="the mode to run pytentd in - multi, single, or both")

def pytest_generate_tests(metafunc):
    """Apply the --mode option to the app fixture"""
    if 'app' in metafunc.fixturenames:
        metafunc.parametrize('app', {
            'multi': (MULTIPLE,),
            'single': (SINGLE,),
            'both': (MULTIPLE, SINGLE),
        }[metafunc.config.option.mode], indirect=True, scope="module")
    
def pytest_runtest_call(item):
    """Log each test"""
    log.info("Running {}".format(item.obj.__name__))

def pytest_runtest_teardown(item, nextitem):
    """If the app fixture was used, clear the database after the test"""
    if 'app' in item.fixturenames:
        log.debug("Dropping collections")
        for collection in collections:
            collection.drop_collection()

@fixture
def app(request):
    """Create an instance of the Tentd app prepared for testing

    The scope for this fixture is defined in pytest_generate_tests"""
    configuration = DEFAULT_APP_CONFIGURATION.copy()
    if request.param == SINGLE:
        configuration['SINGLE_USER_MODE'] = "single_user_name"

    app = create_app(configuration)
    app.client = app.test_client()

    # Setup a request and application context
    ctx = app.test_request_context()
    ctx.push()
    request.addfinalizer(ctx.pop)

    log.info("Created pytentd application[{}]".format(request.param))

    return app

@fixture(scope="function")
def entity(request, app):
    return Entity.new(
        name=app.single_user_mode or 'testuser',
        identity= "http://example.com",
        servers=["http://tent.example.com"]).save()
