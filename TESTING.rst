=======
Testing
=======

Fixtures
========

    - app - ``create_app()`` and then ``clean_database()``
    - Entity (app)
    - Follower (app, follower)
    - client / secure_client (app)

Methods
=======

Using ``current_app``:

    - ``base_url``
    - GET/POST/PUT/HEAD

Test Cases
==========

    - TentdTestCase (app) Will this keep the same app throughout?
