import pytest
from app import app as flask_app  # Importa a instância do Flask do seu arquivo app.py

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Welcome' in response.get_data(as_text=True)

# Mais testes podem ser adicionados aqui
