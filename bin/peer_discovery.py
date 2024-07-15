'''
This is a simple implementation of a peer discovery module
It allows nodes to register themselves with a central registry server and get a list of other nodes

Neetre 2024
'''

import requests
import logging

class PeerDiscovery:
    def __init__(self, registy_url):
        self.registry_url = registy_url
        self.known_peers = set()
        
    def register(self, node_url):
        try:
            data = {"url": node_url}
            response = requests.post(f"{self.registry_url}/register", json=data)
            if response.status_code == 200:
                logging.info(f"Successfully registered node {node_url}")
                return response.json()
            else:
                logging.error(f"Failed to register node {node_url}. Status code {response.status_code}")
                return None
        except requests.RequestException as e:
            logging.error(f"Error registering node {node_url}: {str(e)}")
            return None
    
    def get_peers(self):
        try:
            response = requests.get(f"{self.registry_url}/peers")
            if response.status_code == 200:
                new_peers = set(response.json())
                self.known_peers.update(new_peers)
                return list(self.known_peers)
            else:
                logging.error(f"Failed to get peers. Status code: {response.status_code}")
                return list(self.known_peers)
        except requests.RequestException as e:
            logging.error(f"Error getting peers: {str(e)}")
            return list(self.known_peers)
        
    def add_peer(self, peer_url):
        self.known_peers.add(peer_url)
    
    def remove_peer(self, peer_url):
        self.known_peers.discard(peer_url)
