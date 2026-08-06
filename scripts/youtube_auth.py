import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS = "client_secrets.json"
CREDENTIALS_FILE = "credentials.json"


def get_credentials() -> Credentials:
    creds = None
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(CREDENTIALS_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


if __name__ == "__main__":
    creds = get_credentials()
    print("Authentication successful. credentials.json saved.")
    print(f"Token expires at: {creds.expiry}")
