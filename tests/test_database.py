import pytest
from app.database import Database


@pytest.fixture
def db():
    database = Database()
    database.connect()
    yield database
    database.disconnect()


def test_add_user_success(db):
    assert db.add_user("testuser", "test@example.com") is True
    user = db.get_user("testuser")
    assert user is not None
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"


def test_add_user_duplicate(db):
    db.add_user("testuser", "test@example.com")
    assert db.add_user("testuser", "another@example.com") is False
    assert db.add_user("testuser", "another@example.com") is False 


def test_get_user_found(db):
    db.add_user("testuser", "test@example.com")
    user = db.get_user("testuser")
    assert user is not None
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"


def test_get_user_not_found(db):
    user = db.get_user("nonexistent")
    assert user is None


def test_delete_user_success(db):
    db.add_user("testuser", "test@example.com")
    assert db.delete_user("testuser") is True
    assert db.get_user("testuser") is None


def test_delete_user_not_found(db):
    assert db.delete_user("nonexistent") is False
