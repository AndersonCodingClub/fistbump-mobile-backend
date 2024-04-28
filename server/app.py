import os
import pytz
import base64
from datetime import date
from streak import Streak
from database import Database
from dotenv import load_dotenv
from save import save_post, save_profile_picture
from flask import Flask, request, jsonify, send_from_directory


load_dotenv('config.env')
app = Flask(__name__)
app.static_folder = 'media'

# Server status services
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'msg': 'PONG'})

# User services
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
    
@app.route('/get-user-info/<user_id>')
def get_user_info(user_id):
    try:
        d = Database()
        user_row = d.get_user_row(user_id)
        post_count = len(d.get_posts(user_id))
        follower_count, following_count = len(d.get_followers(user_id)), len(d.get_following(user_id))
        streak = Streak.handle_streak(user_id, False)
        profile_picture_path = d.get_profile_picture(user_id)
        return jsonify({'msg': 'SUCCESS', 
                        'name': user_row[1], 
                        'username': user_row[2], 
                        'followerCount': follower_count, 
                        'followingCount': following_count, 
                        'postCount': post_count, 
                        'streak': streak,
                        'profilePicture': profile_picture_path})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/get-streak/<user_id>')
def get_user_streak(user_id):
    try:
        return {'streak': Streak.handle_streak(user_id, False)}
    except Exception as e:
        print(e)
        return jsonify({'msg':'ERROR'}), 500

# Matching services
@app.route('/get-match', methods=['POST'])
def get_match():
    try:
        d = Database()        
        user_id = int(request.json['userID'])
        
        match_row = d.get_match_row(user_id)

        if match_row and (date.today() - match_row[-1].date()).days == 0:
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

# Image services
@app.route('/save-post', methods=['POST'])
def save_user_post():
    try:
        data = request.json
        
        user_id, match_user_id, image_data_url = data['userID'], data['matchUserID'], data['imageData']
        decoded_data = base64.b64decode(image_data_url.encode('utf-8'))

        path = save_post(decoded_data)
        post_id = Database().add_post(user_id, match_user_id, path)
        Streak.handle_streak(user_id, True)
        Streak.handle_streak(match_user_id, True)
        if post_id:
            return jsonify({'msg': 'SUCCESS'})
        else:
            return jsonify({'msg': 'FAILED'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/get-posts')
def get_user_posts():
    try:
        post_rows = Database().get_posts()
        post_paths = [post_row[3] for post_row in post_rows]
        post_paths.reverse()
        return jsonify({'msg': 'SUCCESS', 'image_paths': post_paths})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/save-profile-picture', methods=['POST'])
def save_user_profile_picture():
    try:
        data = request.json
        
        user_id, image_data_url = data['userID'], data['imageData']
        decoded_data = base64.b64decode(image_data_url.encode('utf-8'))
        
        path = save_profile_picture(decoded_data, user_id)
        Database().set_profile_picture(user_id, path)
        return jsonify({'msg': 'SUCCESS'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/serve/<path:img_path>')
def serve_media(img_path):
    path_components = img_path.split('/')
    directory = f'{path_components[0]}/{path_components[1]}'
    file_name = path_components[2]
    
    return send_from_directory(directory, file_name)

@app.route('/serve/<path:img_path>/metadata')
def serve_media_metadata(img_path):
    try:
        d = Database()
        post_row = d.get_post_row(img_path)
        user1_id, user2_id, date_published = post_row[1], post_row[2], post_row[-1]
        user1_username, user2_username = d.get_user_row(user1_id)[2], d.get_user_row(user2_id)[2]
        
        if os.environ.get('ON_SERVER', 'True') == 'True':
            utc_zone = pytz.utc
            cst_zone = pytz.timezone('America/Chicago')
            date_published_utc = utc_zone.localize(date_published)
            date_published_cst = date_published_utc.astimezone(cst_zone)
        else:
            date_published_cst = date_published
        
        formatted_date = date_published_cst.strftime('%Y-%m-%d %I:%M %p')
        
        return jsonify({'msg': 'SUCCESS', 'user1_id': user1_id, 'user2_id': user2_id, 'user1_name': user1_username, 'user2_name': user2_username, 'date_published': formatted_date})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500

# Follow services
@app.route('/get-followers/<user_id>')
def get_followers(user_id):
    try:
        d = Database()
        follower_ids = d.get_followers(user_id)
        follower_rows = [d.get_user_row(follower_id) for follower_id in follower_ids]
        formatted_follower_rows = []
        for follower_row in follower_rows:
            follower_info_dict = {'user_id': follower_row[0], 'name':follower_row[1], 'username':follower_row[2]}
            formatted_follower_rows.append(follower_info_dict)

        return jsonify({'msg': 'SUCCESS', 'follower_info':formatted_follower_rows})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/get-following/<user_id>')
def get_following(user_id):
    try:
        d = Database()
        following_ids = d.get_following(user_id)
        following_rows = [d.get_user_row(following_id) for following_id in following_ids]
        formatted_following_rows = []
        for following_row in following_rows:
            following_info_dict = {'user_id': following_row[0], 'name':following_row[1], 'username':following_row[2]}
            formatted_following_rows.append(following_info_dict)

        return jsonify({'msg': 'SUCCESS', 'follower_info':formatted_following_rows})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/check-following-status', methods=['POST'])
def check_following_status():
    try:
        data = request.json
        d = Database()
        
        viewer_user_id, status_for_user_id = int(data['viewerUserID']), int(data['userID'])
        follower_user_ids = d.get_followers(status_for_user_id)
        
        return jsonify({'msg': 'SUCCESS', 'isFollowing': viewer_user_id in follower_user_ids})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/follow', methods=['POST'])
def follow_user():
    try:
        data = request.json
        follower_id, following_id = data['followerID'], data['followingID']
        Database().add_follower(follower_id, following_id)
        
        return jsonify({'msg': 'SUCCESS'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
    
@app.route('/unfollow', methods=['POST'])
def unfollow_user():
    try:
        data = request.json
        follower_id, following_id = data['followerID'], data['followingID']
        Database().remove_follower(follower_id, following_id)
        
        return jsonify({'msg': 'SUCCESS'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'ERROR'}), 500
        
if __name__ == '__main__':
    app.run(host=os.environ['HOST'], port=int(os.environ['PORT']), debug=True)