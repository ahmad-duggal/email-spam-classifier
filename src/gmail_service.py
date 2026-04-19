import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define API Scopes: We only need read-only access to emails for classification
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self):
        # Resolve paths relative to where this module is (the 'src' directory)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.credentials_path = os.path.join(base_dir, 'credentials.json')
        self.token_path = os.path.join(base_dir, 'token.json')
        self.service = None

    def authenticate(self):
        """Authenticates the user using OAuth2 and stores token.json."""
        creds = None
        
        # Check if we already have a valid token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception:
                pass
                
        # If no valid token, force re-authentication
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = self._run_auth_flow()
            else:
                creds = self._run_auth_flow()
                
            # Save token for future use
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except HttpError as error:
            print(f"Failed to build Gmail service: {error}")
            return False

    def _run_auth_flow(self):
        if not os.path.exists(self.credentials_path):
             raise FileNotFoundError(f"Missing {self.credentials_path} from project root.")
        # Note: Needs a GUI environment to open browser
        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
        return flow.run_local_server(port=0)

    def fetch_latest_emails(self, max_results=10):
        """Fetches the latest N emails from the INBOX."""
        if not self.service:
            if not self.authenticate():
                raise ConnectionError("Failed to authenticate to Google.")

        results = self.service.users().messages().list(userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        
        email_data_list = []
        
        if not messages:
            return email_data_list
            
        for msg in messages:
            msg_id = msg['id']
            try:
                message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                payload = message.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = "No Subject"
                sender = "Unknown Sender"
                
                for header in headers:
                    if header['name'].lower() == 'subject':
                        subject = header['value']
                    if header['name'].lower() == 'from':
                        sender = header['value']
                        
                # Extract body
                parts = payload.get('parts', [])
                body = "No text content found."
                
                if not parts:
                    data = payload.get('body', {}).get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                else:
                    for part in parts:
                        if part['mimeType'] == 'text/plain':
                            data = part.get('body', {}).get('data')
                            if data:
                                body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break # Just take the first valid text/plain part
                            
                email_data_list.append({
                    "id": msg_id,
                    "sender": sender,
                    "subject": subject,
                    "body": body
                })
            except Exception as e:
                print(f"Error processing email {msg_id}: {str(e)}")
                
        return email_data_list
