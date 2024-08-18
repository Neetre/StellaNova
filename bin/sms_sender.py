import os
from twilio.rest import Client

FROM_SMS = os.environ.get("FROM_SMS")
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(to_sms, code):
    message = client.messages.create(
        to = to_sms,
        from_ = FROM_SMS,
        body = f"{code} is your 2FA code"
    )


if __name__ == "__main__":
    send_sms("+1...", 300293)