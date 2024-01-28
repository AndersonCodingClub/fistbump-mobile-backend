import os
import sys
import json
import socket
import threading
from typing import Tuple
from dotenv import load_dotenv


load_dotenv('config.env')

def handle_client_connection(client_socket: socket.socket, address: Tuple):
    print(f"Connection from {address}")
    try:
        recieved_data = client_socket.recv(1024).decode('utf-8').strip()
        if recieved_data:
            data = json.loads(recieved_data)
            if data['operation'] == 'PING':
                response = {'msg':'PONG'}
            
            client_socket.sendall(bytes(json.dumps(response), encoding='utf-8'))
    except Exception as e:
        print(e)
        response = {'msg':'ERROR'}
        client_socket.sendall(bytes(json.dumps(response), encoding='utf-8'))
    finally:
        client_socket.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('binding...')
    s.bind((os.environ['HOST'], int(os.environ['PORT'])))
    print('listening...')
    s.listen()
    while True:
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        client_thread.start()