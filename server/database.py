import os
import hashlib
import random as rd
import mysql.connector
from typing import List, Tuple


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
            CREATE TABLE IF NOT EXISTS images (
                image_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                path VARCHAR(255) NOT NULL,
                date_published DATETIME NOT NULL
            )
        ''')
        
        self.conn.commit()

    def _close_connection(self):
        self.cursor.close()
        self.conn.close()
    
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
    
    def get_random_user(self, user_id: int) -> int:
        self._setup_connection()
        
        self.cursor.execute('SELECT user_id FROM users')
        user_ids = [row[0] for row in self.cursor.fetchall() if row[0] != user_id]
        
        self._close_connection()
        return rd.choice(user_ids)
    
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

    def add_image(self, user_id: int, path: str) -> int:
        self._setup_connection()
        
        insert_query = 'INSERT INTO images (user_id, path, date_published) VALUES (%s, %s, CURRENT_TIMESTAMP)'
        row = (user_id, path)
        self.cursor.execute(insert_query, row)
        self.conn.commit()
        image_id = self.cursor.lastrowid
        
        self._close_connection()
        return image_id
    
    def get_images(self, user_id: int=None) -> List[Tuple]:
        self._setup_connection()
        
        if user_id:
            self.cursor.execute('SELECT * FROM images WHERE user_id=%s', (user_id,))
        else:
            self.cursor.execute('SELECT * FROM images')
        rows = self.cursor.fetchall()
        
        self._close_connection()
        return rows