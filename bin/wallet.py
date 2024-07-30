from security import Security
from config import COIN_VALUE

class Wallet():

    trans_keys = ['sender', 'recipient', 'amount']

    def __init__(self, id, name, surname, username, tell, email, password, country):
        self.__id = id
        self.__name = name
        self.__surname = surname
        self.__username = username
        self.__tell = tell
        self.__email = email
        self.__country = country
        self.__enc_password = Security.generate(password)
        self.__key_pair = None
        self.__verified_email = False

        self.__balance = 0 # cash
        self.__cypto_balance = [] # transaction, invested
    
    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, new_id):
        self.__id = new_id

    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, new_name):
        self.__name = new_name

    @property
    def surname(self):
        return self.__surname
    
    @surname.setter
    def surname(self, new_surname):
        self.__surname = new_surname

    @property
    def tell(self):
        return self.__tell
    
    @tell.setter
    def tell(self, new_tell):
        self.__tell = new_tell

    @property
    def username(self):
        return self.__username
    
    @username.setter
    def username(self, username):
        self.__username = username
    
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, new_email):
        self.__email = new_email
    
    @property
    def country(self):
        return self.__country
    
    @country.setter
    def country(self, new_country):
        self.__country = new_country

    @property
    def password(self):
        return self.__enc_password
    
    @property
    def key_pair(self):
        if self.__key_pair is None:
            return None
        return self.__key_pair
    
    @key_pair.setter
    def key_pair(self):
        self.__key_pair = Security.generate_key_pair(self.__enc_password)
    
    @property
    def verified_email(self):
        return self.__verified_email
    
    @verified_email.setter
    def verified_email(self, new_status):
        self.__verified_email = new_status

    @property
    def balance(self):
        return self.__balance
    
    @balance.setter
    def balance(self, amount):  # add some type of auth
        if amount == 0:
            return False
        else:
            self.__balance += amount
            return True

    @property
    def cypto_balance(self):
        return self.__cypto_balance
    
    def add_trans_to_balance(self, transaction):
        if self.verify_transaction(transaction):
            self.__cypto_balance.append(transaction)
            return True
        else:
            return False
        
    def get_cash(self):
        tot_coins = 0
        tot_coins = [tot_coins+transaction['amount'] for transaction in self.__cypto_balance][0]
        money = tot_coins * COIN_VALUE  # how to get this?
        self.__balance += money
        self.__cypto_balance = []
        
    def verify_transaction(self, transaction):
        if transaction.keys() in Wallet.trans_keys:
            return True
        else:
            return False
