import pytest
from app.main import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_app_arranque(client):
    """Verifica que la aplicación arranca y responde en la ruta raíz."""
    response = client.get('/', follow_redirects=False)
    # Debe redirigir a /login si no hay sesión iniciada
    assert response.status_code in (200, 302)

def test_login_carga_correctamente(client):
    """Verifica que la vista de login responde con status 200 y formulario."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Inicio de Sesi" in response.data or b"login" in response.data.lower()

