import os
import json
import socket
from typing import Dict


TEST_HOST='127.0.0.1'
TEST_PORT=3000

def send_request(payload: Dict) -> Dict:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TEST_HOST, TEST_PORT))
        s.sendall(bytes(json.dumps(payload), encoding="utf-8"))
        response = s.recv(1024).decode('utf-8').strip()
    return json.loads(response)

def test_client_ping():
    payload = {'operation':'PING'}
    response = send_request(payload=payload)
    
    assert response['msg'] == 'PONG'