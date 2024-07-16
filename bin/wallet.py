
class Wallet():
    def __init__(self):
        self.__username = ""
        self.__email = ""
        self.__password = ""
        self.__key_pair = ()
        
    @property
    def username(self):
        return self.__username
    
    @username.setter
    def set_username(self, username):
        self.__username = username
    
    @property
    def email(self):
        return self.__email
    
    @property
    def password(self):
        return self.__password
    
    @property
    def key_pair(self):
        return self.__key_pair