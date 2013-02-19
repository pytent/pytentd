"""py.test conftest file"""

from flask import g
from py.test import fixture

from tentd import create_app
from tentd.documents import collections, Entity, Post, Follower

#: Constant values for various modes
SINGLE = 'single user mode'
MULTIPLE = 'multiple user mode'
SUBDOMAINS = 'subdomain multiple user mode'

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
            'domains': (SUBDOMAINS),
            'both': (SINGLE, MULTIPLE, SUBDOMAINS),
        }[metafunc.config.option.mode], indirect=True, scope="module")

def pytest_runtest_teardown(item, nextitem):
    """If the app fixture was used, clear the database after the test"""
    if 'app' in item.fixturenames:
        for collection in collections:
            collection.drop_collection()

@fixture
def app(request):
    """Create an instance of the Tentd app prepared for testing

    The scope for this fixture is defined in pytest_generate_tests"""

    single_user_mode, use_subdomains = False, False
    
    if request.param is SINGLE:
        single_user_mode = 'the_single_user'
    elif request.param is SUBDOMAINS:
        use_subdomains = True

    app = create_app({
        'DEBUG': True,
        'TESTING': True,
        'TRAP_HTTP_EXCEPTIONS': True,
        'PRESERVE_CONTEXT_ON_EXCEPTION': False,
        'SERVER_NAME': 'example.com',
        'MONGODB_SETTINGS': {
            'db': 'tentd-testing',
        },
        'SINGLE_USER_MODE': single_user_mode,
        'USE_SUBDOMAINS': use_subdomains,
    })

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
