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
                email VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                major VARCHAR(255),
                year INT,
                streak INT NOT NULL DEFAULT 0
            )
        ''')
        
        self.conn.commit()

    def _close_connection(self):
        self.cursor.close()
        self.conn.close()
    
    def add_user(self, email: str, name: str, username: str, password: str, major: str, year: int) -> int:
        self._setup_connection()
        
        insert_query = 'INSERT INTO users (email, name, username, password, major, year) VALUES (%s, %s, %s, %s, %s, %s)'
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        row = (email, name, username, password_hash, major, year)
        self.cursor.execute(insert_query, row)
        self.conn.commit()
        user_id = self.cursor.lastrowid
        
        self._close_connection()
        return user_id
    
    def validate_user(self, username: str, password: str) -> int:
        self._setup_connection()
        self.cursor.execute('SELECT * FROM users WHERE username=%s OR email=%s', (username, username))
        row = self.cursor.fetchone()
        self._close_connection()
        if row:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == row[4]:
                return row[0]
            
    def check_if_avaliable(self, email: str, username: str) -> bool:
        self._setup_connection()
        
        self.cursor.execute('SELECT * FROM users WHERE username=%s OR email=%s', (username, email))
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