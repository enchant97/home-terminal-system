"""
source:
https://gitlab.com/patkennedy79/flask_user_management_example/
"""

from datetime import datetime
from os import environ

import pytest

from hts import create_app, db
from hts.database.dao.user import new_account
from hts.database.models.user import User


@pytest.fixture(scope='module')
def new_user():
    user = User(
        username="testuser123",
        birthday=datetime.now())
    user.set_password("testuser123")
    return user

@pytest.fixture(scope='module')
def test_client():
    environ["FLASK_CONFIGURATION"] = "test"
    flask_app = create_app()

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()
    # Insert user data
    new_account("user1", "user1", datetime.now())
    new_account("user2", "user2", datetime.now())
    yield db
    db.drop_all()
