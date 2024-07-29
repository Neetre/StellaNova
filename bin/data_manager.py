'''
Tables:
- Security, loggs all the user's old account settings;
- Accounts, loggs all the user's new account settings;
- Transactions, loggs transactions
...

'''

import sqlite3
import time


class DB_manager:
    def __init__(self, db_name="../data/Stellanova.db") -> None:
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        
    def initialize_database(self):
        self.create_Wallet_table()
        self.create_Security_table()
        self.create_Transaction_table()
        self.create_Balance_table()

    def create_Wallet_table(self):
        self.execute_sql_command("""
        CREATE TABLE IF NOT EXISTS wallet (
            id PRIMARY KEY,
            username TEXT,
            name TEXT,
            surname TEXT,
            tell TEXT,
            email TEXT,
            country TEXT,
            enc_password TEXT,
            key_pair TEXT,
            verified_email BOOL
        )
        """)

    def create_Security_table(self):
        self.execute_sql_command("""
        CREATE TABLE IF NOT EXISTS security (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            password TEXT NOT NULL,
            wallet_id TEXT NOT NULL,
            FOREIGN KEY(wallet_id) REFERENCES wallet(id)
        )
        """)

    def create_Transaction_table(self):
        self.execute_sql_command("""
        CREATE TABLE IF NOT EXISTS transaction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction BLOB,
            wallet_id TEXT,
            FOREIGN KEY(wallet_id) REFERENCES wallet(id)
        )
        """)

    def create_Balance_table(self):
        self.execute_sql_command("""
        CREATE TABLE IF NOT EXISTS balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cash INTEGER,
            coins FLOAT,
            wallet_id TEXT,
            FOREIGN KEY(wallet_id) REFERENCES wallet(id)
        )
        """)

    # can be static? or should I make it self??
    def search_user(self, user_id):
        self.cursor.execute(f"""
        SELECT * FROM wallet WHERE id = '{user_id}'
        """)
        return self.cursor.fetchone()

    def execute_command(self, command):
        try:
            self.cursor.execute(command)
            self.conn.commit()
        except Exception as e:
            print(f"An error occoured: {e}")
