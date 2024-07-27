'''
Neetre 2024
'''

import time
from uuid import uuid4
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from argparse import ArgumentParser
from config import MINING_REWARD
from blockchain import Blockchain
from peer_discovery import PeerDiscovery
from contract import SmartContract
import threading
import logging
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from security import generate_keypair, sign_transaction, verify_signature

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', '')
registry_url = "http://127.0.0.1:5000"  # Replace with your actual registry server URL
peer_discovery = PeerDiscovery(registry_url)


app = Flask(__name__)
api = Api(app)


class NodeInfo(Resource):
    def get(self):
        # Info about current node
        pass


class NodeRegister(Resource):
    def post(self):
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


class NodePeers(Resource):
    def get(self):
        peers = peer_discovery.get_peers()
        return jsonify(peers), 200


class Blockchain(Resource):
    def get(self):
        response = {
            'chain' : blockchain.chain,
            'length' : len(blockchain.chain)
        }
        return jsonify(response), 200


class LatestBlock(Resource):
    def get(self):
        return jsonify(blockchain.last_block), 200


class BlockchainHeight(Resource):
    def get(self):
        # get the current height of the blockchain
        return jsonify({'height': len(blockchain.chain)}), 200


class Mine(Resource):
    def get(self):
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


class Transactions(Resource):
    def post(self):
        try:
            values = request.get_json()
            required = ['sender', 'recipient', 'amount', 'public_key', 'signature']
            if not all(k in values for k in required):
                return jsonify({'error': 'Missing values'}), 400
            
            # Convert the public key from string to key object
            public_key = serialization.load_pem_public_key(
                values['public_key'].encode(),
                backend=default_backend()
            )
            
            # Create the transaction
            transaction = {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount']
            }
            
            # Verify the signature
            signature = bytes.fromhex(values['signature'])
            if verify_signature(transaction, signature, public_key):
                index = blockchain.new_transaction(
                    values['sender'], 
                    values['recipient'], 
                    values['amount'],
                    signature,
                    public_key
                )
                response = {'message': f'Transaction will be added to Block {index}'}
                return jsonify(response), 201
            else:
                return jsonify({'error': 'Invalid signature'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500


class PendingTransactions(Resource):
    def get(self):
        # get all pending transactions in the mempool
        return jsonify(blockchain.current_transactions), 200


class TransactionDetails(Resource):
    def get(self, txid):
        # get details of a specific transaction
        transaction = blockchain.get_transaction(txid)
        if transaction:
            return jsonify(transaction), 200
        else:
            return jsonify({'error': 'Transaction not found'}), 404


class Wallet(Resource):
    def post(self):
        private_key, public_key = generate_keypair()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return jsonify({
            'private_key': private_pem.decode(),
            'public_key': public_pem.decode()
        }), 200


class WalletBalance(Resource):
    def get(self, address):
        # get the balance of a specific address (public_key)
        pass
    
class Contracts(Resource):
    def post(self):
        # Deploy details of a specifric contract
        pass
    
class ContractDetails(Resource):
    def get(self, address):
        # Get details of a specific contract
        pass
    
class ExecuteContract(Resource):
    def post(self, address):
        # Execute a smart contract
        pass

class NetworkStatus(Resource):
    def get(self):
        # get the overall network status
        pass
    
class NetworkSync(Resource):
    def post(self):
        # Manually trigger the network sync
        pass


# Add resources to API
api.add_resource(NodeInfo, '/node/info')
api.add_resource(NodeRegister, '/node/register')
api.add_resource(NodePeers, '/node/peers')
api.add_resource(Blockchain, '/blockchain')
api.add_resource(LatestBlock, '/blockchain/latest')
api.add_resource(BlockchainHeight, '/blockchain/height')
api.add_resource(Mine, '/mine')
api.add_resource(Transactions, '/transactions')
api.add_resource(PendingTransactions, '/transactions/pending')
api.add_resource(TransactionDetails, '/transactions/<string:txid>')
api.add_resource(Wallet, '/wallet')
api.add_resource(WalletBalance, '/wallet/<string:address>/balance')
api.add_resource(Contracts, '/contracts')
api.add_resource(ContractDetails, '/contracts/<string:address>')
api.add_resource(ExecuteContract, '/contracts/<string:address>/execute')
api.add_resource(NetworkStatus, '/network/status')
api.add_resource(NetworkSync, '/network/sync')

if __name__ == '__main__':
    app.run(debug=True)