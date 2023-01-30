from ssl import create_default_context
from smtplib import SMTP_SSL
import os


APP_PASSWORD = os.environ["APP_PASSWORD"]
SMTP_SERVER = os.environ["SMTP_SERVER"]
COMPANY_EMAIL = os.environ["COMPANY_EMAIL"]
COMPANY_NAME = os.environ["COMPANY_NAME"]
CLIENT_EMAIL = os.environ["COMPANY_EMAIL"] 
CLIENT_NAME = os.environ["CLIENT_NAME"]

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
