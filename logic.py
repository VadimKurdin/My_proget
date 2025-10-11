import sqlite3
from logic import *
class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            
            conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,    
                user_name TEXT
                         
                    
            )
        ''') 
            conn.execute('''
            CREATE TABLE IF NOT EXISTS selected (
                user_id INTEGER,
                question_id INTEGER,
                question TEXT,
                
                FOREIGN KEY(user_id) REFERENCES users(user_id)         
            
            )
        ''')

            conn.commit()

    
    def add_user(self, user_id, user_name):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT INTO users VALUES (?, ?)', (user_id, user_name))
            conn.commit()

    def get_users(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM users')
            return [x[0] for x in cur.fetchall()]
            
manager = DB_Manager('questiens.db')

if __name__ == '__main__':
    

    manager.create_tables()
