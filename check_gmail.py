import os
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# הגדרות כלליות
WEBHOOK_URL = "https://hook.eu2.make.com/it6by94n5euvdx6qgi241qfsyxovywc2"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    info = {
        "type": "service_account",
        "project_id": os.environ["PROJECT_ID"],
        "private_key_id": os.environ["PRIVATE_KEY_ID"],
        "private_key": os.environ["PRIVATE_KEY"].replace('\\n', '\n'),
        "client_email": os.environ["CLIENT_EMAIL"],
        "client_id": os.environ["CLIENT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ["CLIENT_CERT_URL"]
    }

    # יצירת ההרשאות
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)

    # impersonation – התחזות למשתמש Gmail בתוך הארגון שלך
    creds = creds.with_subject("fincsops@arboxapp.com")

    # יצירת שירות Gmail
    service = build('gmail', 'v1', credentials=creds)
    return service

def check_new_emails():
    service = get_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(ללא נושא)")
        requests.post(WEBHOOK_URL, json={"subject": subject, "id": msg["id"]})

if __name__ == '__main__':
    check_new_emails()
