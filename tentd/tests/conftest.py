"""py.test conftest file"""

import logging

from flask import g
from py.test import fixture

from tentd import create_app
from tentd.documents import collections, Entity, Follower

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('testing')

#: Constant values for single and multi user modes
MULTIPLE, SINGLE = 'multiple user mode', 'single user mode'

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

    mode = "single_user_name" if request.param is SINGLE else False

    app = create_app({
        'DEBUG': True,
        'TESTING': True,
        'TRAP_HTTP_EXCEPTIONS': True,
        'PRESERVE_CONTEXT_ON_EXCEPTION': False,
        'SERVER_NAME': 'tentd.example.com',
        'MONGODB_SETTINGS': {
            'db': 'tentd-testing',
        },
        'SINGLE_USER_MODE': mode,
    })

    # Create a test client, used with the tentd.tests.HTTP functions
    app.client = app.test_client()

    # Setup a request and application context
    ctx = app.test_request_context()
    ctx.push()
    request.addfinalizer(ctx.pop)

    log.info("Created pytentd application[{}]".format(request.param))

    return app

@fixture
def entity(request, app):
    g.entity = Entity.new(
        name=app.single_user_mode or 'testuser',
        identity= "http://example.com",
        servers=["http://tent.example.com"]).save()

    @request.addfinalizer
    def delete_entity():
        if hasattr(g, 'entity'):
            del g.entity
    
    return g.entity

@fixture
def follower(request, entity):
    """A follower with an identity of http://follower.example.com"""
    follower = Follower(entity=entity, identity='http://follower.example.com')
    request.addfinalizer(lambda: follower.delete())
    return follower.save()
