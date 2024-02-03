import os
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
        user_id = d.validate_user(username=username, password=password)
        if user_id:
            return jsonify({'msg': 'SUCCESS', 'userID': user_id})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500

@app.route('/validate-signup-credentials', methods=['POST'])
def validate_signup_credentials():
    try:
        data = request.json
        d = Database()
        username = data['username']
        is_avaliable = d.check_if_avaliable(username)
        if is_avaliable:
            return jsonify({'msg': 'SUCCESS'})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg':'ERROR'}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        d = Database()
        username = data['username']
        if d.check_if_avaliable(username):
            user_id = d.add_user(data['name'], username, data['password'], data['major'], int(data['year']))
            return jsonify({'msg': 'SUCCESS', 'userID': user_id})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
        
if __name__ == '__main__':
    app.run(host=os.environ['HOST'], port=int(os.environ['PORT']))