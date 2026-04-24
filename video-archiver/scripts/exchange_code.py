#!/usr/bin/env python3
"""
Exchange authorization code for tokens.
"""
import os
import sys
import json

def exchange_code(auth_code):
    """Exchange authorization code for access/refresh tokens."""
    try:
        import requests
    except ImportError:
        print("Error: requests library not found")
        sys.exit(1)
    
    config_dir = os.path.expanduser('~/.openclaw/video-archiver')
    credentials_path = os.path.join(config_dir, 'credentials.json')
    
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    if 'installed' in creds_data:
        client_info = creds_data['installed']
    else:
        client_info = creds_data['web']
    
    client_id = client_info['client_id']
    client_secret = client_info['client_secret']
    
    # Exchange code for tokens
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.json()}")
        sys.exit(1)
    
    tokens = response.json()
    
    # Create token.json in the format google expects
    token_data = {
        'token': tokens['access_token'],
        'refresh_token': tokens.get('refresh_token'),
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': client_id,
        'client_secret': client_secret,
        'scopes': ['https://www.googleapis.com/auth/drive'],
        'expiry': None  # Will be set on first use
    }
    
    token_path = os.path.join(config_dir, 'token.json')
    with open(token_path, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("✅ Authentication successful!")
    print(f"Token saved to: {token_path}")
    print()
    print("You can now send video links to download!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: exchange_code.py <authorization_code>")
        print("Example: exchange_code.py '4/abc123...'")
        sys.exit(1)
    
    exchange_code(sys.argv[1])
