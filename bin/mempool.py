'''
This is a simple mempool implementation for a blockchain

neetre 2024
'''

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
