import os
import json
import socket
import threading
from typing import Tuple
from dotenv import load_dotenv


load_dotenv('config.env')

def handle_client_connection(client_socket: socket.socket, address: Tuple):
    print(f"Connection from {address}")
    recieved_data = client_socket.recv(1024).decode('utf-8').strip()
    if recieved_data:
        data = json.loads(recieved_data)
        print(data)
        
    client_socket.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((os.environ['HOST'], int(os.environ['PORT'])))
    s.listen()
    while True:
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        client_thread.start()