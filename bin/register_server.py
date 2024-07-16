'''
This program is a simple implementation of a blockchain node registration server

Neetre 2024
'''

from flask import Flask, jsonify, request
import logging

app = Flask(__name__)
registered_nodes = set()

@app.route('/register', methods=['POST'])
def register_node():
    values = request.get_json()
    node = values.get('url')
    if node is None:
        return "Error: Please supply a valid node URL", 400
    registered_nodes.add(node)
    response = {
        'message': 'Node registered successfully',
        'total_nodes': list(registered_nodes)
    }
    logging.info(f"Registered node: {node}")
    return jsonify(response), 200

@app.route('/peers', methods=['GET'])
def get_peers():
    return jsonify(list(registered_nodes)), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Run on a different port from your main application
