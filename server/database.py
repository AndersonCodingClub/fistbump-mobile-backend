import os
import hashlib
import random as rd
import mysql.connector
from typing import List, Tuple
from dotenv import load_dotenv


load_dotenv('config.env')

class Database:
    def _setup_connection(self):
        self.conn = mysql.connector.connect(host='localhost', user='root', password=os.environ['DATABASE_PASSWORD'])
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('CREATE DATABASE IF NOT EXISTS fistbump')
        self.cursor.execute('USE fistbump')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                major VARCHAR(255),
                age INT,
                streak INT NOT NULL DEFAULT 0,
                pfp_path VARCHAR(255)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id INT AUTO_INCREMENT PRIMARY KEY,
                user1_id INT NOT NULL,
                user2_id INT NOT NULL,
                status VARCHAR(255) NOT NULL DEFAULT 'pending',
                match_date DATETIME NOT NULL,
                FOREIGN KEY (user1_id) REFERENCES users(user_id),
                FOREIGN KEY (user2_id) REFERENCES users(user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS followers (
                follower_id INT NOT NULL,
                following_id INT NOT NULL,
                PRIMARY KEY (follower_id, following_id),
                FOREIGN KEY (follower_id) REFERENCES users(user_id),
                FOREIGN KEY (following_id) REFERENCES users(user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                match_user_id INT NOT NULL,
                path VARCHAR(255) NOT NULL,
                date_published DATETIME NOT NULL
            )
        ''')
        
        self.conn.commit()

    def _close_connection(self):
        self.cursor.close()
        self.conn.close()
        
    # User methods
    def add_user(self, name: str, username: str, password: str, major: str, age: int) -> int:
        self._setup_connection()
        
        insert_query = 'INSERT INTO users (name, username, password, major, age) VALUES (%s, %s, %s, %s, %s)'
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        row = (name, username, password_hash, major, age)
        self.cursor.execute(insert_query, row)
        self.conn.commit()
        user_id = self.cursor.lastrowid
        
        self._close_connection()
        return user_id
    
    def validate_user(self, username: str, password: str) -> int:
        self._setup_connection()
        self.cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
        row = self.cursor.fetchone()
        self._close_connection()
        if row:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == row[3]:
                return row[0]
            
    def check_if_avaliable(self, username: str) -> bool:
        self._setup_connection()
        
        self.cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
        row = self.cursor.fetchone()
        
        self._close_connection()
        return not bool(row)
            
    def get_user_row(self, user_id: int) -> Tuple:
        self._setup_connection()
        
        self.cursor.execute('SELECT * FROM users WHERE user_id=%s', (user_id,))
        row = self.cursor.fetchone()
        
        self._close_connection()
        return row
    
    def search_users(self, name_to_match: str) -> List[Tuple]:
        self._setup_connection()

        search_term = f'%{name_to_match}%'
        self.cursor.execute("SELECT * FROM users WHERE name LIKE %s OR username LIKE %s", (search_term, search_term))
        rows = self.cursor.fetchall()
        
        self._close_connection()
        return rows
    
    def remove_user(self, user_id: int):
        self._setup_connection()
        self.cursor.execute('DELETE FROM users WHERE user_id=%s', (user_id,))
        self.conn.commit()
        self._close_connection()

    # Post methods
    def add_post(self, user_id: int, match_user_id: int, path: str) -> int:
        self._setup_connection()
        
        insert_query = 'INSERT INTO posts (user_id, match_user_id, path, date_published) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)'
        row = (user_id, match_user_id, path)
        self.cursor.execute(insert_query, row)
        self.conn.commit()
        post_id = self.cursor.lastrowid
        
        self._close_connection()
        return post_id
    
    def get_post_row(self, path: str) -> List[Tuple]:
        self._setup_connection()
        
        self.cursor.execute('SELECT * FROM posts WHERE path=%s', (path,))
        row = self.cursor.fetchone()
        
        self._close_connection()
        return row
    
    def get_posts(self, user_id: int=None) -> List[Tuple]:
        self._setup_connection()
        
        if user_id:
            self.cursor.execute('SELECT * FROM posts WHERE user_id=%s OR match_user_id=%s', (user_id, user_id))
        else:
            self.cursor.execute('SELECT * FROM posts')
        rows = self.cursor.fetchall()
        
        self._close_connection()
        return rows
    
    # Profile picture methods
    def get_profile_picture(self, user_id: int) -> List[Tuple]:
        self._setup_connection()
        
        self.cursor.execute('SELECT pfp_path FROM users WHERE user_id=%s', (user_id,))
        row = self.cursor.fetchone()
        
        self._close_connection()
        if row is not None:
            return row[0]
        else:
            return ''
    
    def set_profile_picture(self, user_id: int, pfp_path: str) -> str:
        self._setup_connection()
        
        self.cursor.execute('UPDATE users SET pfp_path=%s WHERE user_id=%s', (pfp_path, user_id))
        self.conn.commit()
        
        self._close_connection()
        return pfp_path
    
    # Match methods
    def get_random_match_user(self, user_id: int) -> int:
        self._setup_connection()
        
        self.cursor.execute('''
            SELECT user_id FROM users 
            WHERE user_id != %s AND user_id NOT IN (
                SELECT user1_id FROM matches
                UNION
                SELECT user2_id FROM matches
            )
        ''', (user_id,))
        available_users = [row[0] for row in self.cursor.fetchall() if row[0] != user_id]
        
        self._close_connection()
        return rd.choice(available_users)
    
    def add_match(self, user1_id: int, user2_id: int) -> int:
        self._setup_connection()
        
        insert_query = 'INSERT INTO matches (user1_id, user2_id, status, match_date) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)'
        row = (user1_id, user2_id, 'pending')
        self.cursor.execute(insert_query, row)
        self.conn.commit()
        match_id = self.cursor.lastrowid
        
        self._close_connection()
        return match_id
    
    def get_match_row(self, user_id: int) -> List[Tuple]:
        self._setup_connection()
        
        select_query = 'SELECT * FROM matches WHERE user1_id=%s OR user2_id=%s'
        self.cursor.execute(select_query, (user_id, user_id))
        match = self.cursor.fetchone()
        
        self._close_connection()
        return match
    
    def set_match_status_to_done(self, user_id: int):
        self._setup_connection()
        
        self.cursor.execute('UPDATE matches SET status="done" WHERE (user1_id=%s OR user2_id=%s)', (user_id, user_id))
        self.conn.commit()
        
        self._close_connection()
        
    def remove_match_row(self, user_id: int):
        self._setup_connection()
        
        self.cursor.execute('DELETE FROM matches WHERE user1_id=%s OR user2_id=%s', (user_id, user_id))
        self.conn.commit()
        
        self._close_connection()
        
    # Streak methods
    def get_streak(self, user_id: int) -> int:
        self._setup_connection()
        
        self.cursor.execute('SELECT streak FROM users WHERE user_id=%s', (user_id,))
        row = self.cursor.fetchone()
        
        self._close_connection()
        return row[0]
    
    def increment_streak(self, user_id: int) -> int:
        self._setup_connection()
        
        self.cursor.execute('UPDATE users SET streak=streak+1 WHERE user_id=%s', (user_id,))
        self.conn.commit()
        
        self._close_connection()
        return self.get_streak(user_id)
    
    def set_streak(self, user_id: int, value: int) -> int:
        self._setup_connection()
        
        self.cursor.execute('UPDATE users SET streak=%s WHERE user_id=%s', (value, user_id))
        self.conn.commit()
        
        self._close_connection()
        return value
        
    # Follow methods
    def add_follower(self, follower_id: int, following_id: int):
        self._setup_connection()
        
        insert_query = 'INSERT INTO followers (follower_id, following_id) VALUES (%s, %s)'
        self.cursor.execute(insert_query, (follower_id, following_id))
        self.conn.commit()
        
        self._close_connection()

    def remove_follower(self, follower_id: int, following_id: int):
        self._setup_connection()
        
        delete_query = 'DELETE FROM followers WHERE follower_id=%s AND following_id=%s'
        self.cursor.execute(delete_query, (follower_id, following_id))
        self.conn.commit()
        
        self._close_connection()
        
    def get_followers(self, user_id: int) -> List[int]:
        self._setup_connection()
        
        self.cursor.execute('SELECT follower_id FROM followers WHERE following_id=%s', (user_id,))
        followers = [row[0] for row in self.cursor.fetchall()]
        
        self._close_connection()
        return followers
        
    def get_following(self, user_id: int) -> List[int]:
        self._setup_connection()
        
        self.cursor.execute('SELECT following_id FROM followers WHERE follower_id=%s', (user_id,))
        following = [row[0] for row in self.cursor.fetchall()]
        
        self._close_connection()
        return following