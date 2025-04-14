import pytest
from flask import Flask, jsonify
from app.api import api_bp
from app.database import Database
import tempfile
import os
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    app = Flask(__name__)
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True
    app.register_blueprint(api_bp)

    with app.app_context():
        db = Database(app.config['DATABASE'])
        db.connect()
        db.disconnect()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()

def test_test_endpoint(client):
    response = client.get('/api/test')
    assert response.status_code == 200
    assert response.json == {'status': 'API fonctionne correctement'}

# Tests for Calculator Endpoints
def test_add_valid(client):
    response = client.get('/api/add/5/3')
    assert response.status_code == 200
    assert response.json == {'result': 8.0}

def test_add_invalid(client):
    response = client.get('/api/add/five/3')
    assert response.status_code == 400
    assert 'error' in response.json

def test_subtract_valid(client):
    response = client.get('/api/subtract/10/4')
    assert response.status_code == 200
    assert response.json == {'result': 6.0}

def test_subtract_invalid(client):
    response = client.get('/api/subtract/10/four')
    assert response.status_code == 400
    assert 'error' in response.json

def test_multiply_valid(client):
    response = client.get('/api/multiply/6/7')
    assert response.status_code == 200
    assert response.json == {'result': 42.0}

def test_multiply_invalid(client):
    response = client.get('/api/multiply/six/7')
    assert response.status_code == 400
    assert 'error' in response.json

def test_divide_valid(client):
    response = client.get('/api/divide/10/2')
    assert response.status_code == 200
    assert response.json == {'result': 5.0}

def test_divide_by_zero(client):
    response = client.get('/api/divide/10/0')
    assert response.status_code == 400
    assert response.json == {'error': 'Division par zéro impossible'}

def test_divide_invalid(client):
    response = client.get('/api/divide/ten/2')
    assert response.status_code == 400
    assert 'error' in response.json

# Tests for User Management Endpoints
def test_add_user_missing_data(client):
    response = client.post('/api/user', json={'username': 'testuser2'})
    assert response.status_code == 400
    assert response.json == {'error': 'Les champs username et email sont requis'}

def test_add_user_duplicate(client):
    client.post('/api/user', json={'username': 'duplicate', 'email': 'duplicate@example.com'})
    response = client.post('/api/user', json={'username': 'duplicate', 'email': 'duplicate@example.com'})
    assert response.status_code == 409
    assert response.json == {'error': 'Cet utilisateur existe déjà'}

def test_get_user_not_found(client):
    response = client.get('/api/user/nonexistent')
    assert response.status_code == 404
    assert response.json == {'error': 'Utilisateur non trouvé'}

def test_delete_user_found(client):
    client.post('/api/user', json={'username': 'deleteuser', 'email': 'delete@example.com'})
    response = client.delete('/api/user/deleteuser')
    assert response.status_code == 200
    assert response.json == {'message': 'Utilisateur supprimé avec succès'}
    
    get_response = client.get('/api/user/deleteuser')
    assert get_response.status_code == 404

# Quelques tests avec mock ici dans le cadre du TP
@patch('app.api.db')
def test_delete_user_not_found(mock_db, client):
    mock_db.delete_user.return_value = False
    response = client.delete('/api/user/nonexistentdelete')
    assert response.status_code == 404
    assert response.json == {'error': 'Utilisateur non trouvé'}
    mock_db.delete_user.assert_called_once_with('nonexistentdelete')

@patch('app.api.db')
def test_get_user_found(mock_db, client):
    mock_db.get_user.return_value = {'username': 'getuser', 'email': 'get@example.com'}
    response = client.get('/api/user/getuser')
    assert response.status_code == 200
    assert response.json == {'username': 'getuser', 'email': 'get@example.com'}
    mock_db.get_user.assert_called_once_with('getuser')

@patch('app.api.db')
def test_add_user_valid(mock_db, client):
    mock_db.add_user.return_value = True
    response = client.post('/api/user', json={'username': 'testuser', 'email': 'test@example.com'})
    assert response.status_code == 201
    assert response.json == {'message': 'Utilisateur ajouté avec succès'}
    mock_db.add_user.assert_called_once_with('testuser', 'test@example.com')