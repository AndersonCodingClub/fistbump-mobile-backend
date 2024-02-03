import os
import base64
from database import Database
from dotenv import load_dotenv
from save import save_image_file
from flask import Flask, request, jsonify


load_dotenv('config.env')
app = Flask(__name__)
app.static_folder = 'media'

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
            user_id = d.add_user(data['name'], username, data['password'], data['major'], int(data['age']))
            return jsonify({'msg': 'SUCCESS', 'userID': user_id})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/save-image', methods=['POST'])
def save_image():
    try:
        data = request.json
        
        user_id, image_data_url = data['user_id'], data['dataURL']
        image_data = image_data_url.split(',')[1]
        decoded_data = base64.b64decode(image_data.encode('utf-8'))
        
        path = save_image_file(decoded_data)
        image_id = Database().add_image(user_id, path)
        if image_id:
            return jsonify({'msg': 'SUCCESS'})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/get-images', methods=['GET'])
def get_images():
    try:
        image_rows = Database().get_images()
        image_paths = [image_row[2] for image_row in image_rows]
        if image_paths:
            return jsonify({'msg': 'SUCCESS', 'image_paths': image_paths})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
        
if __name__ == '__main__':
    app.run(host=os.environ['HOST'], port=int(os.environ['PORT']))