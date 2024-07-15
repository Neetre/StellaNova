'''
This is the main file that runs the blockchain node.
It is a simple blockchain node that can mine blocks, add transactions, and resolve conflicts with other nodes.
It also has a simple smart contract that can be used to validate transactions.

Neetre 2024
'''

import time
from uuid import uuid4
from flask import Flask, render_template, request, jsonify
from argparse import ArgumentParser
from config import MINING_REWARD
from blockchain import Blockchain, SmartContract
from peer_discovery import PeerDiscovery
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

registry_url = "http://127.0.0.1:5001"  # Replace with your actual registry server URL
peer_discovery = PeerDiscovery(registry_url)

my_node_url = "http://127.0.0.1:5000"  # Replace with your actual node URL
peer_discovery.register(my_node_url)


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
        peer_discovery.add_peer(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/peers', methods=['GET'])
def get_peers():
    peers = peer_discovery.get_peers()
    return jsonify(peers), 200

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

def update_peers_periodically():
    while True:
        peers = peer_discovery.get_peers()
        for peer in peers:
            blockchain.register_node(peer)
        time.sleep(300)


peer_update_thread = threading.Thread(target=update_peers_periodically)
peer_update_thread.start()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)