import os
import base64
from datetime import date
from database import Database
from dotenv import load_dotenv
from save import save_image_file
from flask import Flask, request, jsonify, send_from_directory


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
        username = data['username']
        if Database().check_if_avaliable(username):
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
    
@app.route('/get-match', methods=['POST'])
def get_match():
    try:
        d = Database()        
        user_id = int(request.json['userID'])
        
        match_row = d.get_match_row(user_id)
        match_day_difference = (date.today() - match_row[-1].date()).days

        if match_row and match_day_difference == 0:
            # Return existing match information
            match_user_id = (match_row[1] if match_row[1] != user_id else match_row[2])
            match_user_row = d.get_user_row(match_user_id)
        else:
            # Create new match
            d.remove_match_row(user_id)
            match_user_id = d.get_random_match_user(user_id)
            match_user_row = d.get_user_row(match_user_id)
            d.add_match(user1_id=user_id, user2_id=match_user_id)
        
        return jsonify({'msg': 'SUCCESS', 'match_user_id': match_user_id, 'match_user_row': match_user_row})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/save-image', methods=['POST'])
def save_image():
    try:
        data = request.json
        
        user_id, match_user_id, image_data_url = data['userID'], data['matchUserID'], data['imageData']
        decoded_data = base64.b64decode(image_data_url.encode('utf-8'))

        path = save_image_file(decoded_data)
        image_id = Database().add_image(user_id, match_user_id, path)
        if image_id:
            return jsonify({'msg': 'SUCCESS'})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/get-images')
def get_images():
    try:
        image_rows = Database().get_images()
        image_paths = [image_row[3] for image_row in image_rows]
        if image_paths:
            image_paths.reverse()
            return jsonify({'msg': 'SUCCESS', 'image_paths': image_paths})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/serve/<path:img_path>')
def serve_media(img_path):
    directory, file_name = img_path.split('/')
    return send_from_directory(directory, file_name)
        
if __name__ == '__main__':
    app.run(host=os.environ['HOST'], port=int(os.environ['PORT']), debug=False)