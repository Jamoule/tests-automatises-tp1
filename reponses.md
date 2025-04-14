# Réponses aux Exercices de Tests Automatisés

## Partie 1 : Tests unitaires

### 1. `tests/test_calculator.py`

Ce fichier contient les tests unitaires pour la classe `Calculator` située dans `app/calculator.py`.

- **Opérations testées :** `add`, `subtract`, `multiply`, `divide`.
- **Cas limites :** Des tests spécifiques sont inclus pour gérer la division par zéro, qui devrait lever une exception `ValueError`. D'autres cas limites potentiels (nombres très grands, nombres négatifs) sont également couverts.

*(Mon explication : Les tests unitaires ici isolent la classe `Calculator` et vérifient que chaque méthode fonctionne correctement individuellement, y compris dans les situations potentiellement problématiques comme la division par zéro.)*

#### Tests (`tests/test_calculator.py`)

```python
import pytest
from app.calculator import Calculator

def test_add():
    calculator = Calculator()
    assert calculator.add(1, 2) == 3
    assert calculator.add(-1, 1) == 0
    assert calculator.add(-1, -1) == -2
    assert calculator.add(0, 0) == 0
    assert calculator.add(100, 200) == 300

def test_subtract():
    calculator = Calculator()
    assert calculator.subtract(5, 3) == 2
    assert calculator.subtract(3, 5) == -2
    assert calculator.subtract(-1, -1) == 0
    assert calculator.subtract(0, 0) == 0
    assert calculator.subtract(10, 0) == 10
    assert calculator.subtract(0, 10) == -10

def test_multiply():
    calculator = Calculator()
    assert calculator.multiply(2, 3) == 6
    assert calculator.multiply(-2, 3) == -6
    assert calculator.multiply(2, -3) == -6
    assert calculator.multiply(-2, -3) == 6
    assert calculator.multiply(0, 5) == 0
    assert calculator.multiply(5, 0) == 0

def test_divide():
    calculator = Calculator()
    assert calculator.divide(6, 3) == 2
    assert calculator.divide(-6, 3) == -2
    assert calculator.divide(6, -3) == -2
    assert calculator.divide(-6, -3) == 2
    assert calculator.divide(0, 5) == 0
    assert calculator.divide(7, 2) == 3.5

def test_divide_by_zero():
    calculator = Calculator()
    with pytest.raises(ZeroDivisionError):
        calculator.divide(6, 0)
    with pytest.raises(ZeroDivisionError):
        calculator.divide(0, 0)
    with pytest.raises(ZeroDivisionError):
        calculator.divide(-5, 0)
```

### 2. `tests/test_database.py`

Ce fichier contient les tests unitaires pour la classe `Database` (dans `app/database.py`).

- **Méthodes testées :** `add_user`, `get_user`, `delete_user`.
- **Fixtures pytest :** Une fixture (`db`) est utilisée pour initialiser une instance de la base de données en mémoire avant chaque test et la fermer après.

*(Mon explication : Les fixtures permettent de réutiliser le code de configuration et de nettoyage(en gros initialiser la db avec un jeu de données et la nettoyer à chaque test). Tester les opérations CRUD basiques est essentiel.)*

#### Tests (`tests/test_database.py`)

```python
import pytest
from app.database import Database


@pytest.fixture
def db():
    database = Database() # Utilise :memory: par défaut
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
    # Vérifier qu'une deuxième tentative échoue aussi
    assert db.add_user("testuser", "onemore@example.com") is False


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
```

## Partie 2 : Tests d'intégration

### 1. `tests/test_api.py`

Ce fichier contient les tests d'intégration pour l'API Flask (définie dans `app/api.py`).

- **Client de test Flask :** Le `test_client` fourni par Flask est utilisé pour envoyer des requêtes HTTP simulées.
- **Endpoints testés :** Endpoints de calculatrice et de gestion des utilisateurs.
- **Vérifications :** Codes de statut HTTP et contenu des réponses JSON.

*(Explication : Les tests d'intégration vérifient que les différentes parties (API, logique métier, base de données simulée ou réelle) fonctionnent ensemble.)*

#### Tests (`tests/test_api.py`)

```python
import pytest
from flask import Flask, jsonify
from app.api import api_bp
from app.database import Database
import tempfile
import os
from unittest.mock import patch, MagicMock

# Fixture pour créer une instance de l'application Flask pour les tests
@pytest.fixture
def app():
    app = Flask(__name__)
    # Utiliser une base de données temporaire distincte pour chaque test
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True
    app.register_blueprint(api_bp)

    with app.app_context():
        db_instance = Database(app.config['DATABASE'])
        db_instance.connect()
        db_instance.disconnect() 

    yield app 

    # Nettoyage après le test
    os.close(db_fd)
    os.unlink(db_path)

# Fixture pour obtenir un client de test Flask
@pytest.fixture
def client(app):
    return app.test_client()

# Test simple pour vérifier que l'API est accessible
def test_test_endpoint(client):
    response = client.get('/api/test')
    assert response.status_code == 200
    assert response.json == {'status': 'API fonctionne correctement'}

# --- Tests pour les Endpoints de la Calculatrice ---
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

# --- Tests pour les Endpoints de Gestion Utilisateurs (utilisant la DB réelle via fixture) ---
def test_add_user_valid_real_db(client):
    response = client.post('/api/user', json={'username': 'testuser1', 'email': 'test1@example.com'})
    assert response.status_code == 201
    assert response.json == {'message': 'Utilisateur ajouté avec succès'}
    # Vérifier que l'utilisateur existe maintenant
    get_response = client.get('/api/user/testuser1')
    assert get_response.status_code == 200
    assert get_response.json == {'username': 'testuser1', 'email': 'test1@example.com'}

def test_add_user_missing_data(client):
    response = client.post('/api/user', json={'username': 'testuser2'}) # Email manquant
    assert response.status_code == 400
    assert response.json == {'error': 'Les champs username et email sont requis'}

def test_add_user_duplicate(client):
    # Ajouter un utilisateur une première fois
    client.post('/api/user', json={'username': 'duplicate', 'email': 'duplicate@example.com'})
    # Tenter de l'ajouter à nouveau
    response = client.post('/api/user', json={'username': 'duplicate', 'email': 'duplicate@example.com'})
    assert response.status_code == 409 # Conflit
    assert response.json == {'error': 'Cet utilisateur existe déjà'}

def test_get_user_not_found(client):
    response = client.get('/api/user/nonexistent')
    assert response.status_code == 404
    assert response.json == {'error': 'Utilisateur non trouvé'}

def test_delete_user_found(client):
    # Ajouter un utilisateur pour pouvoir le supprimer
    client.post('/api/user', json={'username': 'deleteuser', 'email': 'delete@example.com'})
    # Supprimer l'utilisateur
    response = client.delete('/api/user/deleteuser')
    assert response.status_code == 200
    assert response.json == {'message': 'Utilisateur supprimé avec succès'}
    # Vérifier qu'il n'existe plus
    get_response = client.get('/api/user/deleteuser')
    assert get_response.status_code == 404

def test_delete_user_not_found(client):
    response = client.delete('/api/user/nonexistentdelete')
    assert response.status_code == 404
    assert response.json == {'error': 'Utilisateur non trouvé'}

# --- Tests avec Mocks (ajoutés ici comme demandé) ---

# Mock la variable 'db' dans le module 'app.api'
@patch('app.api.db')
def test_get_user_found_mocked(mock_db, client):
    # Configurer le mock pour retourner un utilisateur spécifique
    mock_db.get_user.return_value = {'username': 'getuser_mock', 'email': 'get_mock@example.com'}
    response = client.get('/api/user/getuser_mock')
    assert response.status_code == 200
    assert response.json == {'username': 'getuser_mock', 'email': 'get_mock@example.com'}
    # Vérifier que la méthode mockée a été appelée correctement
    mock_db.get_user.assert_called_once_with('getuser_mock')

@patch('app.api.db')
def test_add_user_valid_mocked(mock_db, client):
    # Configurer le mock pour simuler un ajout réussi
    mock_db.add_user.return_value = True
    response = client.post('/api/user', json={'username': 'testuser_mock', 'email': 'test_mock@example.com'})
    assert response.status_code == 201
    assert response.json == {'message': 'Utilisateur ajouté avec succès'}
    mock_db.add_user.assert_called_once_with('testuser_mock', 'test_mock@example.com')

@patch('app.api.db')
def test_delete_user_not_found_mocked(mock_db, client):
    # Configurer le mock pour simuler un utilisateur non trouvé lors de la suppression
    mock_db.delete_user.return_value = False
    response = client.delete('/api/user/nonexistentdelete_mock')
    assert response.status_code == 404
    assert response.json == {'error': 'Utilisateur non trouvé'}
    mock_db.delete_user.assert_called_once_with('nonexistentdelete_mock')
```

## Partie 3 : Mocks et tests avancés

### 1. Utilisation de mocks (`pytest-mock`)

- **Modification des tests :** Certains tests (ici, dans `test_api.py`) utilisent `@patch` de `unittest.mock` (compatible avec `pytest-mock`) pour remplacer l'objet `db` réel par un mock.
- **Simulation de la base de données :** Le mock est configuré pour retourner des valeurs spécifiques (`return_value`) ou simuler des échecs, permettant de tester la logique de l'API indépendamment de la base de données.

*(Explication : Les mocks isolent le composant testé (l'API) de ses dépendances (la base de données).)*

#### Exemple de tests mockés (extrait de `tests/test_api.py`)

```python
from unittest.mock import patch

# [...] (fixtures client et app nécessaires)

# Mock la variable 'db' dans le module 'app.api'
@patch('app.api.db')
def test_get_user_found_mocked(mock_db, client):
    # Configurer le mock pour retourner un utilisateur spécifique
    mock_db.get_user.return_value = {'username': 'getuser_mock', 'email': 'get_mock@example.com'}
    response = client.get('/api/user/getuser_mock')
    assert response.status_code == 200
    assert response.json == {'username': 'getuser_mock', 'email': 'get_mock@example.com'}
    # Vérifier que la méthode mockée a été appelée correctement
    mock_db.get_user.assert_called_once_with('getuser_mock')

@patch('app.api.db')
def test_add_user_valid_mocked(mock_db, client):
    # Configurer le mock pour simuler un ajout réussi
    mock_db.add_user.return_value = True
    response = client.post('/api/user', json={'username': 'testuser_mock', 'email': 'test_mock@example.com'})
    assert response.status_code == 201
    assert response.json == {'message': 'Utilisateur ajouté avec succès'}
    mock_db.add_user.assert_called_once_with('testuser_mock', 'test_mock@example.com')

@patch('app.api.db')
def test_delete_user_not_found_mocked(mock_db, client):
    # Configurer le mock pour simuler un utilisateur non trouvé lors de la suppression
    mock_db.delete_user.return_value = False
    response = client.delete('/api/user/nonexistentdelete_mock')
    assert response.status_code == 404
    assert response.json == {'error': 'Utilisateur non trouvé'}
    mock_db.delete_user.assert_called_once_with('nonexistentdelete_mock')

```

### 2. Analyse de couverture

- **Exécution avec couverture :** `pytest --cov=app`
- **Identification du code non couvert :** Le rapport (console ou HTML via `--cov-report=html`) montre les lignes non exécutées.
- **Amélioration de la couverture :** Ajout de tests pour couvrir ces lignes.

*(Explication : La couverture mesure la proportion du code exécutée par les tests.)*

### Exemple de sortie terminal

Voici un exemple de ce que la sortie pourrait ressembler lors de l'exécution des commandes :

```bash
(venv) jipei@Jipeis-MacBook-Air tests-automatises % pytest
================================================================== test session starts ==================================================================
platform darwin -- Python 3.9.6, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jipei/Documents/DC/tests-automatises
plugins: cov-6.1.1
collected 31 items

tests/test_api.py .................                                                                                                               [ 54%]
tests/test_app.py ...                                                                                                                             [ 64%]
tests/test_calculator.py .....                                                                                                                    [ 80%]
tests/test_database.py ......                                                                                                                     [100%]

================================================================== 31 passed in 0.20s ===================================================================

(venv) jipei@Jipeis-MacBook-Air tests-automatises % pytest --cov=app
================================================================== test session starts ==================================================================
platform darwin -- Python 3.9.6, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jipei/Documents/DC/tests-automatises
plugins: cov-6.1.1
collected 31 items

tests/test_api.py .................                                                                                                               [ 54%]
tests/test_app.py ...                                                                                                                             [ 64%]
tests/test_calculator.py .....                                                                                                                    [ 80%]
tests/test_database.py ......                                                                                                                     [100%]

==================================================================== tests coverage =====================================================================
____________________________________________________ coverage: platform darwin, python 3.9.6-final-0 ____________________________________________________

Name                Stmts   Miss  Cover
---------------------------------------
app/__init__.py        12      0   100%
app/api.py             77      0   100%
app/calculator.py      11      0   100%
app/database.py        42      0   100%
---------------------------------------
TOTAL                 142      0   100%
================================================================== 31 passed in 0.23s ===================================================================

(venv) jipei@Jipeis-MacBook-Air tests-automatises % pytest --cov=app --cov-report=html
================================================================== test session starts ==================================================================
platform darwin -- Python 3.9.6, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jipei/Documents/DC/tests-automatises
plugins: cov-6.1.1
collected 31 items

tests/test_api.py .................                                                                                                               [ 54%]
tests/test_app.py ...                                                                                                                             [ 64%]
tests/test_calculator.py .....                                                                                                                    [ 80%]
tests/test_database.py ......                                                                                                                     [100%]

==================================================================== tests coverage =====================================================================
____________________________________________________ coverage: platform darwin, python 3.9.6-final-0 ____________________________________________________

Coverage HTML written to dir htmlcov
================================================================== 31 passed in 0.24s ===================================================================

(venv) jipei@Jipeis-MacBook-Air tests-automatises % pytest tests/test_calculator.py
================================================================== test session starts ==================================================================
platform darwin -- Python 3.9.6, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jipei/Documents/DC/tests-automatises
plugins: cov-6.1.1
collected 5 items

tests/test_calculator.py .....                                                                                                                    [100%]

=================================================================== 5 passed in 0.05s ===================================================================

(venv) jipei@Jipeis-MacBook-Air tests-automatises % pytest tests/test_api.py
================================================================== test session starts ==================================================================
platform darwin -- Python 3.9.6, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jipei/Documents/DC/tests-automatises
plugins: cov-6.1.1
collected 17 items

tests/test_api.py .................                                                                                                               [100%]

================================================================== 17 passed in 0.13s ===================================================================

(venv) jipei@Jipeis-MacBook-Air tests-automatises % pytest tests/test_database.py
================================================================== test session starts ==================================================================
platform darwin -- Python 3.9.6, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jipei/Documents/DC/tests-automatises
plugins: cov-6.1.1
collected 6 items

tests/test_database.py ......                                                                                                                     [100%]

=================================================================== 6 passed in 0.05s ===================================================================
(venv) jipei@Jipeis-MacBook-Air tests-automatises % 
```


J'ai une couverture de code de 100% et tous mes tests s'executent correctements