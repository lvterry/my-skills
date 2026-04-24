#!/usr/bin/env python3
"""
Generate Google Drive OAuth URL for manual authorization.
"""
import os
import sys
import json

def generate_auth_url():
    """Generate OAuth URL for user to visit."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Error: Google API libraries not found.")
        sys.exit(1)
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    config_dir = os.path.expanduser('~/.openclaw/video-archiver')
    credentials_path = os.path.join(config_dir, 'credentials.json')
    
    if not os.path.exists(credentials_path):
        print(f"Error: credentials.json not found")
        sys.exit(1)
    
    # Load credentials to get client info
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    if 'installed' in creds_data:
        client_info = creds_data['installed']
    elif 'web' in creds_data:
        client_info = creds_data['web']
    else:
        print("Error: Invalid credentials format")
        sys.exit(1)
    
    client_id = client_info['client_id']
    redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # Out-of-band / manual
    
    # Build auth URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=https://www.googleapis.com/auth/drive&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    print("=" * 60)
    print("Google Drive Authorization")
    print("=" * 60)
    print()
    print("1. Open this URL in your browser:")
    print()
    print(auth_url)
    print()
    print("2. Sign in and authorize the application")
    print()
    print("3. Copy the authorization code and send it to me")
    print("   (It should look like: 4/xxxxx...)")
    print()
    print("=" * 60)
    
    # Save client secret for later use
    return client_info

if __name__ == '__main__':
    generate_auth_url()
