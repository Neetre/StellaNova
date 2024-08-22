'''
This is a simple security module that provides functions for generating keypairs, signing transactions, verifying signatures,


Neetre 2024
'''

import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization

import numpy as np

import data_manager
from email_sender import send_email
from email_templates import security_settigs_change_subject, security_settigs_change_body


class Security:
    def __init__(self) -> None:
        pass

    # Base operations on password
    @staticmethod
    def generate(password):
        key = Security.generate_key()
        Security.save_key(key)
        
        enc_pwd = Security.encrypt_password(password, key)
        
        return enc_pwd
    
    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    @staticmethod
    def encrypt_password(password, key):
        f = Fernet(key)
        encrypted_password = f.encrypt(password.encode("utf-8"))
        return encrypted_password
    
    @staticmethod
    def decrypt_password(enc_password, key):
        f = Fernet(key)
        dec_password = f.decrypt(enc_password).decode("utf-8")
        return dec_password
    
    @staticmethod
    def save_key(key):
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)
            
    @staticmethod
    def load_key():
        return open('secret.key', 'rb').read()
    
    # Stuff for transactions
    @staticmethod
    def generate_key_pair(password):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode('utf-8'))
        )
        
        return pem, public_key

    @staticmethod
    def decode_pem(pem_data, password):
        private_key = serialization.load_pem_private_key(
            pem_data,
            password=password.encode("utf-8"),
            backend=default_backend()
        )
        return private_key


    @staticmethod
    def sign_transaction(transaction, pem, password):
        transaction_bytes = json.dumps(transaction, sort_keys=True).encode("utf-8")
        private_key = Security.decode_pem(pem, password)
        signature = private_key.sign(
            transaction_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    @staticmethod
    def verify_signature(transaction, signature, public_key):
        transaction_bytes = json.dumps(transaction, sort_keys=True).encode("utf-8")
        try:
            public_key.verify(
                signature,
                transaction_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    # 2FA
    @staticmethod
    def generate_2FA_code():
        # 6 cifers, random
        code = np.random.randint(100000, 999999)
        return code


class ModSecurity:
    def __init__(self, to_email: str, user_id, username: str):
        self.to_email = to_email
        self.user_id = user_id
        self.username = username
        self.current_change = None
        self.changes = None

    def check_account(self):
        old_settings, new_settings = data_manager.search_user(self.user_id)  # probably going to a sql DB or to a search engine
        changes = self.find_changes(old_settings, new_settings)

        if changes is []:
            self.changes = changes
            return True
        else:
            self.changes = changes
            return True
    
    def find_changes(old_settings: dict, new_settings: dict):
        changes = []
        for key in old_settings:
            if old_settings[key] == new_settings[key]:
                continue
            else:
                changes.append(new_settings[key])

        return changes

    def notify_change(self, change):
        self.current_change = change
        self.send_security_email()

    def send_security_email(self):
        send_email(self.to_email, security_settigs_change_subject, security_settigs_change_body.format(self.username, self.changes))

    def MOD(self):
        did_change = self.check_account()
        if did_change:
            self.send_security_email()
            return True
        
        return False
    

if __name__ == "__main__":
    mod = ModSecurity("test@sium.com", "IG2394SS...", "Pippo")
    did_change = mod.MOD()
    if did_change:
        print("Erm, changed")
    else:
        print("All good")
