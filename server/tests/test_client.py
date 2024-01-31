import requests
from typing import Dict


TEST_HOST='0.0.0.0'
TEST_PORT=3000
TEST_URL = f'http://{TEST_HOST}:{TEST_PORT}'

def _make_post_request(payload: Dict, endpoint: str) -> requests.Response:
    headers = {'Content-Type': 'application/json'}
    return requests.post(f'{TEST_URL}/{endpoint}', json=payload, headers=headers)

def test_client_ping():
    resp = requests.get(f'{TEST_URL}/ping')
    
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'PONG'
    
def test_valid_client_login():
    payload = {'username':'testuser', 'password':'testuserpassword'}
    resp = _make_post_request(payload, 'login') 
    
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'SUCCESS'
    
def test_invalid_client_login():
    payload = {'username':'invalidtestuser', 'password':'invalidtestpassword'}
    resp = _make_post_request(payload, 'login') 
       
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'FAILED'