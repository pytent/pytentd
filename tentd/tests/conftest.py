"""py.test conftest file"""

from flask import g
from mongoengine.connection import ConnectionError
from py.test import fixture, exit

from tentd import create_app
from tentd.documents import collections, Entity, Post, Follower, Following

def pytest_addoption(parser):
    """Add an option to chose the modes tests will be run under"""
    parser.addoption('--mode', action='store', default='subdomain',
        help="the mode to run in (multiple, single, subdomain, all)")

def pytest_generate_tests(metafunc):
    """Apply the --mode option to the app fixture"""
    if 'app' in metafunc.fixturenames:
        metafunc.parametrize('app', {
            'multiple': ('MULTIPLE',),
            'single': ('SINGLE',),
            'subdomain': ('SUBDOMAIN',),
            'all': ('MULTIPLE', 'SINGLE', 'SUBDOMAIN'),
        }[metafunc.config.option.mode], indirect=True, scope="module")

def pytest_runtest_teardown(item, nextitem):
    """If the app fixture was used, clear the database after the test"""
    if 'app' in item.fixturenames:
        for collection in collections:
            collection.drop_collection()

def pytest_runtest_makereport (item, call):
    """Stop the tests early when we can't connect to the database"""
    if hasattr(call.excinfo, 'type'):
        if call.excinfo.type == ConnectionError:
            exit("Could not connect to the database")

@fixture
def app(request):
    """Create an instance of the Tentd app prepared for testing

    The scope for this fixture is defined in pytest_generate_tests"""

    config = {
        'DEBUG': True,
        'TESTING': True,
        'TRAP_HTTP_EXCEPTIONS': True,
        'PRESERVE_CONTEXT_ON_EXCEPTION': False,
        'SERVER_NAME': 'example.com',
        'MONGODB_SETTINGS': {
            'db': 'tentd-testing',
        },
        'USER_MODE': request.param,
    }

    if request.param == 'SINGLE':
        config['USER_NAME'] = 'the_single_user'
        
    app = create_app(config)

    # Create a test client, used with the tentd.tests.HTTP functions
    app.client = app.test_client()

    # Make the test mode availible, not useful for much more than debugging
    app.test_mode = request.param

    # Setup a request and application context
    ctx = app.test_request_context()
    ctx.push()
    request.addfinalizer(ctx.pop)

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
def post(request, entity):
    """A post with multiple versions"""
    schema = 'https://tent.io/types/post/status/v0.1.0'
    post = Post(entity=entity, schema=schema)
    post.new_version(
        content={
            'text': "Hello world",
            'coordinates': [0, 0],
        },
        mention=[])
    post.new_version(
        content={
            'text': "How are you, world?",
            'coordinates': [1, 1],
        },
        mention=[])
    post.new_version(
        content={
            'text': "Goodbye world",
            'coordinates': [2, 2]},
        mentions=[{
            'entity': 'http://softly.example.com'
        }])
    post.save()

    # Fetch the post from the database,
    # so that the version ordering is correct
    post = Post.objects.get(entity=entity, schema=schema)
    request.addfinalizer(post.delete)
    return post

@fixture
def follower(request, entity):
    """A follower with an identity of http://follower.example.com"""
    follower = Follower(
        entity=entity,
        identity='http://follower.example.com',
        servers=['http://follower.example.com/tentd'],
        notification_path='notification')
    request.addfinalizer(follower.delete)
    return follower.save()

@fixture
def following(request, entity):
    """A following with an identity of http://following.example.com"""
    following = Following(
        entity=entity,
        identity='http://following.example.com')
    request.addfinalizer(following.delete)
    return following.save()
