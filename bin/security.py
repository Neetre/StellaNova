'''
This is a simple security module that provides functions for generating keypairs, signing transactions, and verifying signatures

Neetre 2024
'''

import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def generate_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def sign_transaction(transaction, private_key):
    transaction_bytes = json.dumps(transaction, sort_keys=True).encode()
    signature = private_key.sign(
        transaction_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(transaction, signature, public_key):
    transaction_bytes = json.dumps(transaction, sort_keys=True).encode()
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
