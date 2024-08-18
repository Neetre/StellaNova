import os
import json
from security import Security
from dotenv import load_dotenv
load_dotenv()
from email_sender import send_email
from email_templates import verification_code_subject, verification_code_body
from sms_sender import send_sms


class MFA():
    def __init__(self, username: str, to_email: str, stats_file="../data/stats.json"):
        self.stats_file = stats_file
        self.is_code_ok = False
        self.username = username
        self.to_email = to_email

    def load_stats(self):
        stats = json.load(open(self.stats_file, "r"))
        return stats
    
    def save_code(self, new_code):
        with open("../data/old_codes.b", "ab") as file:
            file.write(new_code.encode('utf-8'))

    def read_codes(self):
        with open("../data/old_codes.b", "rb") as file:
            reader = file.readlines()
        return reader

    def check_new_code(self, code):
        reader = self.read_codes()
        for old_code in reader[-20:]:
            if old_code.decode("utf-8") == code:
                return False
            
        return True
    
    def mfa_email(self, code: int):
        send_email(self.to_email, verification_code_subject, verification_code_body.format(self.username, code))

    def MFA(self):
        '''
        This function does all the process for the
        2FA verification
        '''
        while not self.is_code_ok:
            code = Security.generate_2FA_code()
            self.is_code_ok = self.check_new_code(code)
            if self.is_code_ok:
                self.save_code(code)
                break

        self.mfa_email(code)


class SMS:
    def __init__(self, cell) -> None:
        self.is_code_ok = False
        self.cell = cell

    def save_code(self, new_code):
        with open("../data/old_codes.b", "ab") as file:
            file.write(new_code.encode('utf-8'))

    def read_codes(self):
        with open("../data/old_codes.b", "rb") as file:
            reader = file.readlines()
        return reader

    def check_new_code(self, code):
        reader = self.read_codes()
        for old_code in reader[-20:]:
            if old_code.decode("utf-8") == code:
                return False
            
        return True
    
    def SMS(self, to_cell):
        while not self.is_code_ok:
            code = Security.generate_2FA_code()
            self.is_code_ok = self.check_new_code(code)
            if self.is_code_ok:
                break

        send_sms(to_cell, code)



if __name__ == "__main__":
    Mfa = MFA("test@gmail.com", "Pippo")
    Mfa.MFA()
