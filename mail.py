from ssl import create_default_context
from smtplib import SMTP_SSL

# TODO: add and use these variables from the environment
APP_PASSWORD = "onticbqwrozfajpb"
SMTP_SERVER = "smtp.gmail.com"
COMPANY_EMAIL = "ahmed4h.gawish@gmail.com" 
COMPANY_NAME = "SCDR"
CLIENT_EMAIL = "amgawish@student.aast.edu" 
CLIENT_NAME = "French Dude"

PORT = 465

def send_email(message):
    email = f"""From: {COMPANY_NAME} <{COMPANY_EMAIL}>
To: {CLIENT_NAME} <{CLIENT_EMAIL}>
Subject: New Hermes Products Notfication
{message}
"""
    context = create_default_context()
    with SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(COMPANY_EMAIL, APP_PASSWORD)
        server.sendmail(COMPANY_EMAIL, CLIENT_EMAIL, email)
