from app import app
from policyai.core import chunk_text

def test_health():
    with app.test_client() as client:
        response=client.get('/health')
        assert response.status_code==200
        assert response.json['status']=='ok'

def test_home():
    with app.test_client() as client:assert client.get('/').status_code==200

def test_chunking():
    chunks=chunk_text('abc '*1000)
    assert len(chunks)>1
    assert all(len(chunk)<=1100 for chunk in chunks)
