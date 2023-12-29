from fastapi.testclient import TestClient
from asyncww import app



def test_count_queue():
    with TestClient(app) as client:
        response = client.get('/count')
        assert response.status_code == 200


def test_handle_start():
    with TestClient(app) as client:
        for i in range(1000):
            response = client.get(f'/start/{i}')
            assert response.status_code == 200


def test_handle_stop():
    with TestClient(app) as client:
        for i in range(1000):
            response = client.get('/stop')
            assert response.status_code == 200
