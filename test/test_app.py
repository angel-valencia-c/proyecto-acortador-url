# tests/test_app.py
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['DB_NAME']        = ':memory:'
os.environ['ADMIN_PASSWORD'] = 'testpass'
os.environ['SECRET_KEY']     = 'test-secret-key'

from app import app
from database import init_db

@pytest.fixture
def client():
    """Cliente de prueba con BD en memoria."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_home_carga(client):
    """La página principal responde 200."""
    r = client.get('/')
    assert r.status_code == 200

def test_crear_url(client):
    """Crear URL retorna short_id."""
    r = client.post('/crear',
        json={'original_url': 'https://google.com'},
        content_type='application/json'
    )
    assert r.status_code == 200
    assert 'short_id' in r.get_json()

def test_redireccion_valida(client):
    """Un short_id válido redirige correctamente."""
    r = client.post('/crear',
        json={'original_url': 'https://google.com'},
        content_type='application/json'
    )
    short_id = r.get_json()['short_id']
    r2 = client.get(f'/{short_id}')
    assert r2.status_code == 302

def test_redireccion_inexistente(client):
    """Un short_id inexistente retorna 404."""
    r = client.get('/noexiste')
    assert r.status_code == 404

def test_dashboard_requiere_login(client):
    """Dashboard redirige si no hay sesión."""
    r = client.get('/reportes')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']

def test_exportar_excel_requiere_login(client):
    """/exportar-excel requiere login."""
    r = client.get('/exportar-excel')
    assert r.status_code == 302

def test_exportar_csv_requiere_login(client):
    """/exportar-csv requiere login."""
    r = client.get('/exportar-csv')
    assert r.status_code == 302

def test_toggle_requiere_login(client):
    """/toggle requiere login."""
    r = client.post('/toggle/abc123')
    assert r.status_code == 302

def test_login_incorrecto(client):
    """Password incorrecto muestra error."""
    r = client.post('/login', data={'password': 'wrong'})
    assert b'incorrecta' in r.data

def test_login_correcto(client):
    """Password correcto redirige al dashboard."""
    r = client.post('/login', data={'password': 'testpass'})
    assert r.status_code == 302