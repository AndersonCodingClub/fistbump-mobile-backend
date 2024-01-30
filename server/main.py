import os
import json
from flask import Flask, request, jsonify
from database import Database
from dotenv import load_dotenv


load_dotenv('config.env')
app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'msg': 'PONG'})

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username, password = data['username'], data['password']
        d = Database()
        if d.validate_user(username=username, password=password):
            return jsonify({'msg': 'SUCCESS'})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
if __name__ == '__main__':
    app.run(host=os.environ['HOST'], port=int(os.environ['PORT']))