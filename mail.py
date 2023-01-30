from ssl import create_default_context
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
import os


APP_PASSWORD = os.environ["APP_PASSWORD"]
SMTP_SERVER = os.environ["SMTP_SERVER"]
COMPANY_EMAIL = os.environ["COMPANY_EMAIL"]
COMPANY_NAME = os.environ["COMPANY_NAME"]
CLIENT_EMAIL = os.environ["COMPANY_EMAIL"] 
CLIENT_NAME = os.environ["CLIENT_NAME"]

PORT = 465

def send_email(text):
    message = MIMEText(text, 'plain', 'utf-8')
    message['Subject'] = "New Hermes Products Notifications"
    message['From'] = COMPANY_EMAIL
    message['To'] = CLIENT_EMAIL 
    context = create_default_context()
    with SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(COMPANY_EMAIL, APP_PASSWORD)
        server.send_message(COMPANY_EMAIL, CLIENT_EMAIL, message)

