#!/usr/bin/env python3
"""
Create folder in Google Drive and save folder ID to config.
"""
import os
import sys
import json
from datetime import datetime, timedelta

def create_folder(folder_name="Downloaded Videos"):
    """Create folder in Google Drive and return its ID."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        print("Error: Google API libraries not found")
        sys.exit(1)
    
    config_dir = os.path.expanduser('~/.openclaw/video-archiver')
    token_path = os.path.join(config_dir, 'token.json')
    credentials_path = os.path.join(config_dir, 'credentials.json')
    
    # Load token
    if not os.path.exists(token_path):
        print("Error: token.json not found. Please authenticate first.")
        sys.exit(1)
    
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    # Create credentials from token data
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    
    # Refresh if needed
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            token_data['token'] = creds.token
            with open(token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
        else:
            print("Error: Credentials invalid and cannot be refreshed")
            sys.exit(1)
    
    service = build('drive', 'v3', credentials=creds)
    
    # Check if folder already exists
    results = service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    
    items = results.get('files', [])
    
    if items:
        folder_id = items[0]['id']
        print(f"✅ Folder '{folder_name}' already exists")
    else:
        # Create folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(body=file_metadata, fields='id, name').execute()
        folder_id = folder.get('id')
        print(f"✅ Created folder '{folder_name}'")
    
    # Save folder ID to config
    config_path = os.path.join(config_dir, 'config.json')
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    config['folder_id'] = folder_id
    config['folder_name'] = folder_name
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📁 Folder ID: {folder_id}")
    print(f"💾 Config saved to: {config_path}")
    print(f"\nVideos will be uploaded to: {folder_name}")
    
    return folder_id

if __name__ == '__main__':
    folder_name = sys.argv[1] if len(sys.argv) > 1 else "Downloaded Videos"
    create_folder(folder_name)
