import os
import hashlib
import random as rd
import mysql.connector
from typing import List, Tuple


os.environ['password'] = '$uper$trong2007!'

class Database:
    def _setup_connection(self):
        self.conn = mysql.connector.connect(host='localhost', user='root', password=os.environ['password'])
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
                streak INT NOT NULL DEFAULT 0
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
            CREATE TABLE IF NOT EXISTS images (
                image_id INT AUTO_INCREMENT PRIMARY KEY,
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

    # Image methods
    def add_image(self, user_id: int, match_user_id: int, path: str) -> int:
        self._setup_connection()
        
        insert_query = 'INSERT INTO images (user_id, match_user_id, path, date_published) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)'
        row = (user_id, match_user_id, path)
        self.cursor.execute(insert_query, row)
        self.conn.commit()
        image_id = self.cursor.lastrowid
        
        self._close_connection()
        return image_id
    
    def get_image_row(self, path: str) -> List[Tuple]:
        self._setup_connection()
        
        self.cursor.execute('SELECT * FROM images WHERE path=%s', (path,))
        row = self.cursor.fetchone()
        
        self._close_connection()
        return row
    
    def get_images(self, user_id: int=None) -> List[Tuple]:
        self._setup_connection()
        
        if user_id:
            self.cursor.execute('SELECT * FROM images WHERE user_id=%s', (user_id,))
        else:
            self.cursor.execute('SELECT * FROM images')
        rows = self.cursor.fetchall()
        
        self._close_connection()
        return rows
    
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