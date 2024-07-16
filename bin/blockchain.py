'''
This program is a simple blockchain implementation with a proof of work algorithm.

Neetre 2024
'''

import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests
import logging
from config import PROOF_OF_WORK_DIFFICULTY
from security import verify_signature
from mempool import Mempool


class Blockchain():
    def __init__(self) -> None:
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.mempool = Mempool()
        self.smart_contracts = {}
        self.balances = {}
        
        # create the genesis block
        self.new_block(previous_hash=1, proof=100)
        
    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        transactions = self.mempool.get_transactions(10)
        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : time(),
            'transactions' : transactions,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1])
        }
        
        # Reset the current list of transactions
        self.mempool.remove_transactions(transactions)
        self.current_transactions = []
        self.chain.append(block)
        
        return block
    
    def new_transaction(self, sender, recipient, amount, signature=None, public_key=None):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }
        if signature and public_key:
            if verify_signature(transaction, signature, public_key):
                if self.check_balance(transaction):
                    self.update_balances(transaction)
                    self.mempool.add_transaction(transaction)
                    return self.last_block['index'] + 1
                else:
                    raise ValueError("Insufficient balance")
            else:
                raise ValueError("Invalid transaction signature")
        else:
            if self.check_balance(sender, amount):
                self.update_balances(transaction)
                self.mempool.add_transactions(transaction)
                return self.last_block['index'] + 1
            else:
                raise ValueError("Insufficient balance")
            
    def check_balance(self, account, amount):
        return account == "0" or (account in self.balances and self.balances[account] >= amount)
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    def update_balances(self, transaction):
        sender = transaction['sender']
        recipient = transaction['recipient']
        amount = transaction['amount']
        
        if sender != "0":  # "0" is used for mining rewards
            if sender not in self.balances or self.balances[sender] < amount:
                raise ValueError("Insufficient balance")
            self.balances[sender] -= amount
            
        self.balances[recipient] = self.balances.get(recipient, 0) + amount
    
    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def proof_or_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
        :param last_block: <dict> last Block
        :return: <int>
        """
        logging.info(f"Starting proof of work for block {last_block['index']}")
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        logging.info(f"Proof of work completed. Proof: {proof}")
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:len(PROOF_OF_WORK_DIFFICULTY)] == PROOF_OF_WORK_DIFFICULTY
    
    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        try:
            parsed_url = urlparse(address)
            if parsed_url.netloc:
                self.nodes.add(parsed_url.netloc)
            elif parsed_url.path:
                self.nodes.add(parsed_url.path)
            else:
                raise ValueError('Invalid URL')
        except Exception as e:
            logging.error(f"Error registering node {address}: {str(e)}")
            raise
    
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1
        
        while current_index < len(chain):
            block = chain[current_index]

            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")

            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], block['previous_hash']):
                return False
            
            if block['timestamp'] <= last_block['timestamp']:
                return False
            
            for transaction in block['transactions']:
                if not self.valid_transaction(transaction):
                    return False

            last_block = block
            current_index += 1
            
        return True
    
    def valid_transaction(self, transaction):
        # This is a basic check. In a real implementation, you'd want to check things like:
        # - Does the sender have enough balance?
        # - Is the transaction signature valid?
        # - Is the transaction format correct?
        return all(k in transaction for k in ['sender', 'recipient', 'amount'])
    
    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        
        for node in neighbours:
            response = requests.get(f'http//{node}/chain')
            
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        if new_chain:
            self.chain = new_chain
            return True
        
        return False
    
    def add_smart_contract(self, contract):
        contract_address = hashlib.sha256(contract.code.encode()).hexdigest()
        self.smart_contracts[contract_address] = contract
        return contract_address
    
    def execute_smart_contract(self, contract_address, transaction):
        contract = self.smart_contracts.get(contract_address)
        if contract:
            return contract.execute(self, transaction)
        return False
