from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import mail

"""
READ ALSO:
https://medium.com/better-programming/a-beginners-guide-to-the-google-gmail-api-and-its-documentation-c73495deff08
"""


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailService:

    def __init__(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_path = ""
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def send_mail(self, recipent, subject, message_text):
        message = mail.CreateMessage("me", recipent, subject, message_text)
        response = mail.SendMessage(self.service, "me", message)
        print(str(response))

    def send_mail_with_attachment(self, recipent, subject, message_text, file_dir, filename):
        message = mail.CreateMessageWithAttachment("me", recipent, subject, message_text, file_dir, filename)
        response = mail.SendMessage(self.service, "me", message)
        print(str(response))