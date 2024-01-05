from fastapi.testclient import TestClient
from fastapi_proxy import app, settings


def test_status():
    with TestClient(app) as client:
        response = client.get("/start_tg")
        assert response.status_code == 404
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json() == {'banned_till': None, 'messages_waited': 0}


def test_send_queue():
    with TestClient(app) as client:
        response = client.get("/start_tg")
        assert response.status_code == 404
        for i in range(100, 150):
            response = client.get(f"/endpoint_method/{1111}")
            assert response.status_code == 200
            assert response.json()['count'] <= 30


def test_len_queue():
    with TestClient(app) as client:
        count = 0
        for i in range(100, 220):
            response = client.get(f"/endpoint_method/{1111}")
            assert response.status_code == 200
            count = max(response.json()['count'], count)
        print(count)
        assert count <= 30