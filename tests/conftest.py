import pytest
from app import app
import uuid
from models import guard, User

@pytest.fixture
def test_app():
    test_app = app
    test_app.config.update({
        'TESTING': True,
    })
    yield test_app

@pytest.fixture
def test_db(test_app):
    from models import db
    with test_app.app_context():
        yield db

@pytest.fixture
def client(test_app):
    return test_app.test_client()

@pytest.fixture
def runner(test_app):
    return test_app.test_cli_runner()

@pytest.fixture
def user(test_db):
    userid = str(uuid.uuid4())
    test_user = User(id=userid, email="test@test.com", name='Test V', username="test",
                    hashed_password=guard.hash_password('password'))
    test_db.session.add(test_user)
    test_db.session.commit()
    yield userid
    u = User.query.get(userid)
    if u:
        test_db.session.delete(test_user)
        test_db.session.commit()

