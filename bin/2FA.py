import os
import json
from email_sender import send_email
from email_templates import verification_code_subject, verification_code_body
from security import Security
from dotenv import load_dotenv
load_dotenv()


class MFA():
    def __init__(self, stats_file="../data/stats.json"):
        self.stats_file = stats_file
        self.is_code_ok = False

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
        for old_code in reader[-10:]:
            if old_code.decode("utf-8") == code:
                return False
            
        return True

    def MFA(self):
        while not self.is_code_ok:
            code = Security.generate_2FA_code()
            self.is_code_ok = self.check_new_code(code)
            if self.is_code_ok:
                self.save_code(code)
                break

        return code
