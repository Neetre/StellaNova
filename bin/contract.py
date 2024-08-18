'''
This is a simple smart contract implementation for a blockchain

Neetre 2024
'''

class SmartContract:
    
    list_of_contracts = []
    
    def __init__(self, code):
        self.code = code
        self.__address = None
        SmartContract.list_of_contracts.append(self)

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
    
    @property
    def address(self):
        return self.__address
    
    @address.setter
    def address(self, address):
        self.__address = address
