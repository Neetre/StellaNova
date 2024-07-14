'''
This program is a simple blockchain implementation with a proof of work algorithm.
It also includes a simple smart contract system that allows users to add and execute
smart contracts on the blockchain.

The blockchain is implemented as a Flask application with the following endpoints:
- /mine: mine a new block
- /transactions/new: create a new transaction
- /chain: get the full blockchain
- /nodes/register: register a new node
- /nodes/resolve: resolve conflicts between nodes

Neetre 2024
'''

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, render_template, request, jsonify
from argparse import ArgumentParser
import logging
from config import PROOF_OF_WORK_DIFFICULTY, MINING_REWARD
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Blockchain(object):
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


class Mempool:
    def __init__(self):
        self.transactions = []
        
    def add_transactions(self, transaction: object):
        self.transactions.append(transaction)
        
    def get_transactions(self, n):
        return self.transactions[:n]
    
    def remove_transactions(self, transactions):
        for transaction in transactions:
            if transaction in self.transactions:
                self.transactions.remove(transaction)


class PeerDiscovery:
    def __init__(self, registy_url):
        self.registry_url = registy_url
        
    def register(self, node_url):
        data = {"url": node_url}
        response = requests.post(f"{self.registry_url}/register", json=data)
        return response.json()
    
    def get_peers(self):
        response = requests.get(f"{self.registry_url}/peers")
        return response.json()


class SmartContract:
    def __init__(self, code):
        self.code = code

    def execute(self, blockchain, transaction):
        # This is a very simplified execution environment
        # In a real implementation, you'd need a proper virtual machine
        global_vars = {
            'blockchain': blockchain,
            'transaction': transaction,
            'approve': lambda: True,
            'reject': lambda: False
        }
        exec(self.code, global_vars)
        return global_vars.get('result', False)


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

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instatiate the Blockchain
blockchain = Blockchain()

simple_contract = """
if transaction['amount'] > 100:
    result = reject()
else:
    result = approve()
"""
    
contract = SmartContract(simple_contract)
contract_address = blockchain.add_smart_contract(contract)

# peer_discovery = PeerDiscovery("http://registry-server-url")
# my_url = "http://my_node_url"
# peer_discovery.register(my_url)

# peers = peer_discovery.get_peers()
# for peer in peers:
#     blockchain.register_node(peer)

@app.route('/')
def index():
    return render_template('index.html', chain=blockchain.chain)

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_or_work(last_block)
    
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=MINING_REWARD,
    )
    
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    try:
        values = request.get_json()
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return jsonify({'error': 'Missing values'}), 400
        
        # Add signature verification here if implemented
        index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
        response = {'message': f'Transaction will be added to Block {index}'}
        return jsonify(response), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    
    if replaced:
        response = {
            'message' : 'Our chain was replaced',
            'new_chain' : blockchain.chain
        }
    else:
        response = {
            'message' : 'Our chain is authoritative',
            'chain' : blockchain.chain
        }
    return jsonify(response), 200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)