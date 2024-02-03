import os
import sys
import requests
from typing import Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'server')))

from database import Database


TEST_HOST='10.9.150.219'
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
    
def test_validate_valid_client_signup_credentials():
    payload = {'username':'avaliabletestuser'}
    resp = _make_post_request(payload, 'validate-signup-credentials')
    
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'SUCCESS'
    
def test_validate_invalid_client_signup_credentials():
    payload = {'username':'testuser'}
    resp = _make_post_request(payload, 'validate-signup-credentials')
    
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'FAILED'

def test_valid_client_signup():
    payload = {'username':'testsignup', 'password':'testsignuppassword', 'name':'Test Signup', 'major':'major', 'age':21}
    resp = _make_post_request(payload, 'signup')
    
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'SUCCESS'
    
    db = Database()
    db.remove_user(resp.json()['userID'])
    
def test_invalid_client_signup():
    db = Database()
    user_id = db.add_user('Test Signup', 'testsignup', 'testsignuppassword', 'major', 21)
    
    payload = {'username':'testsignup', 'password':'testsignuppassword', 'name':'Test Signup', 'major':'major', 'age':21}
    resp = _make_post_request(payload, 'signup')
    
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'FAILED'
    
    db = Database()
    db.remove_user(user_id)