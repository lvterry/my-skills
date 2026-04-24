#!/usr/bin/env python3
"""
Google Drive Authentication Setup
Run this once to authenticate with Google Drive.
"""
import os
import sys

def setup_auth():
    """Run OAuth flow to get Google Drive credentials."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Error: Google API libraries not found.")
        print("Install with: python3 -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        sys.exit(1)
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    config_dir = os.path.expanduser('~/.openclaw/video-archiver')
    os.makedirs(config_dir, exist_ok=True)
    
    token_path = os.path.join(config_dir, 'token.json')
    credentials_path = os.path.join(config_dir, 'credentials.json')
    
    if not os.path.exists(credentials_path):
        print(f"Error: credentials.json not found in {config_dir}")
        print("\nTo set up Google Drive access:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 credentials (Desktop application type)")
        print("5. Download the credentials.json file")
        print(f"6. Place it at: {credentials_path}")
        print("\nThen run this script again.")
        sys.exit(1)
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print(f"✅ Authentication successful!")
        print(f"Token saved to: {token_path}")
        print("You can now upload videos to Google Drive.")
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    setup_auth()
