# tests/test_app.py
import pytest
from flask import Flask
from app import create_app
import os 

def test_create_app_no_config():
    app = create_app()
    assert app is not None
    assert app.config['SECRET_KEY'] == 'dev'
    assert app.config['DATABASE'] == 'app.db'
    assert not app.config.get('TESTING', False)

def test_create_app_with_config():
    test_config = {
        'TESTING': True,
        'DATABASE': 'test_override.db',
        'CUSTOM_KEY': 'custom_value'
    }
    app = create_app(test_config)
    assert app is not None
    assert app.config['TESTING'] is True
    assert app.config['DATABASE'] == 'test_override.db'
    assert app.config['CUSTOM_KEY'] == 'custom_value'

@pytest.fixture
def client():
    db_path = 'test_client.db'
    app = create_app({'TESTING': True, 'DATABASE': db_path})
    with app.test_client() as client:
        yield client
    if os.path.exists(db_path):
        os.remove(db_path)


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"L'application fonctionne. Essayez /api/add/2/3" in response.data 