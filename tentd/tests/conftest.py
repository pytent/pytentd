"""py.test conftest file"""

from flask import _request_ctx_stack
from py.test import fixture
from werkzeug import ImmutableDict

from tentd import create_app
from tentd.documents import collections, Entity

def drop_collections():
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

@fixture(scope="class", params=[False, True])
def app(request):
    """An instance of the Tentd app"""
    configuration = DEFAULT_APP_CONFIGURATION.copy()
    if request.param:
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

    if not request.config.option.quiet:
        print "Created tentd application",
        print "(single user mode)" if app.single_user_mode else ""
    
    return app

@fixture(scope="class")
def entity(request, app):
    entity = Entity.new(
        name=app.single_user_mode or 'testuser',
        identity= "http://example.com",
        servers=["http://tent.example.com"])
    
    return entity.save()
