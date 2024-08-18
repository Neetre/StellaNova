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
        self.create_Blocks_table()
        self.create_Transaction_table()
        self.create_Mempool_table()
        self.create_Contract_table()
        self.create_Peer_table()
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
            enc_password TEXT NOT NULL,
            wallet_id TEXT NOT NULL,
            FOREIGN KEY(wallet_id) REFERENCES wallet(id)
        )
        """)
        
    def create_Blocks_table(self):
        self.execute_sql_command('''
            CREATE TABLE IF NOT EXISTS Blocks (
                block_hash TEXT PRIMARY KEY,
                previous_hash TEXT,
                nonce INTEGER,
                timestamp TEXT,
                transactions TEXT
            )
        ''')

    def create_Transaction_table(self):
        self.execute_sql_command('''
            CREATE TABLE IF NOT EXISTS Transactions (
                transaction_id INTEGER PRIMARY KEY,
                sender_address TEXT,
                recipient_address TEXT,
                amount FLOAT,
                timestamp TEXT,
                public_key TEXT,
                signature TEXT
            )
        ''')

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
        
    def create_Contract_table(self):
        self.execute_sql_command('''
            CREATE TABLE IF NOT EXISTS Contracts (
                contract_id INTEGER PRIMARY KEY,
                code TEXT,
                address TEXT,
                timestamp TEXT
            )
        ''')
        
    def create_Peer_table(self):
        self.execute_sql_command('''
            CREATE TABLE IF NOT EXISTS Peers (
                peer_id INTEGER PRIMARY KEY,
                ip_address TEXT,
                port INTEGER,
                public_key TEXT,
            )
        ''')
        
    def insert_wallet(self, public_key, private_key, balance, username, email, password):
        self.execute_sql_command(f'''
            INSERT INTO Wallet (public_key, private_key, balance, username, email, password)
            VALUES ('{public_key}', '{private_key}', {balance}, '{username}', '{email}', '{password}')
        ''')
    
    def insert_block(self, block_hash, previous_hash, nonce, timestamp, transactions):
        self.execute_sql_command(f'''
            INSERT INTO Blocks (block_hash, previous_hash, nonce, timestamp, transactions)
            VALUES ('{block_hash}', '{previous_hash}', {nonce}, '{timestamp}', '{transactions}')
        ''')

    # can be static? or should I make it self??
    def search_user(self, user_id):
        self.cursor.execute(f"""
        SELECT * FROM wallet WHERE id = '{user_id}'
        """)
        return self.cursor.fetchone()
    
    def search_key(self, enc_password):
        self.cursor.execute(f"""
        SELECT * FROM security WHERE enc_password = '{enc_password}'
        """)
        pwd = self.cursor.fetchone()
        return pwd[1]

    def execute_command(self, command):
        try:
            self.cursor.execute(command)
            self.conn.commit()
        except Exception as e:
            print(f"An error occoured: {e}")
