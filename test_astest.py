from fastapi.testclient import TestClient

from astest import app

client = TestClient(app)



def get_status():
    print('status')
    response = client.get('/statis')
    assert response.status_code == 200
