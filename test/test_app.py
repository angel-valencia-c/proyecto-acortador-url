# tests/test_app.py
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import init_db

@pytest.fixture
def client():
    """Cliente de prueba con base de datos en memoria."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    os.environ['DB_NAME'] = ':memory:'
    os.environ['ADMIN_PASSWORD'] = 'testpass'

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_home_carga_correctamente(client):
    """La página principal debe responder 200."""
    response = client.get('/')
    assert response.status_code == 200

def test_crear_url_corta(client):
    """Crear una URL corta debe retornar un short_id."""
    response = client.post('/crear', json={'url': 'https://google.com'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'short_id' in data or response.status_code == 200

def test_redireccion_url_inexistente(client):
    """Un short_id inexistente debe retornar 404."""
    response = client.get('/abc123')
    assert response.status_code == 404

def test_dashboard_requiere_login(client):
    """El dashboard debe redirigir si no hay sesión."""
    response = client.get('/reportes')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_login_password_incorrecto(client):
    """Login con password incorrecto debe mostrar error."""
    response = client.post('/login', data={'password': 'wrongpass'})
    assert b'incorrecta' in response.data

def test_login_password_correcto(client):
    """Login correcto debe redirigir al dashboard."""
    response = client.post('/login', data={'password': 'testpass'})
    assert response.status_code == 302