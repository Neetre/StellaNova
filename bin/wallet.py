from security import Security

class Wallet():
    def __init__(self, id, name, surname, tell, email, password, country):
        self.__id = id
        self.__name = name
        self.__surname = surname
        self.__tell = tell
        self.__email = email
        self.__country = country
        self.__enc_password = Security.generate(password)
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, new_id):
        self.__id = new_id

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
    def password(self):
        return self.__enc_password
    
    @property
    def key_pair(self):
        return self.__key_pair