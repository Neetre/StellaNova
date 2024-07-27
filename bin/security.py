'''
This is a simple security module that provides functions for generating keypairs, signing transactions, and verifying signatures

Neetre 2024
'''

import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization


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
    def decrypt_password(password, key):
        f = Fernet(key)
        dec_password = f.decrypt(password).decode("utf-8")
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
    def sign_transaction(self, transaction, pem, password):
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
    def verify_signature(self, transaction, signature, public_key):
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
    def email_verific(self):
        pass