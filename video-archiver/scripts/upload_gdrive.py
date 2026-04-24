#!/usr/bin/env python3
"""
Upload videos to Google Drive.
"""
import os
import sys
import json

def upload_to_drive(file_path, title=None, folder_id=None):
    """
    Upload a file to Google Drive.
    Returns dict with: success, file_id, url, error
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        return {
            'success': False,
            'error': 'Google API libraries not found. Install: python3 -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client'
        }
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    config_dir = os.path.expanduser('~/.openclaw/video-archiver')
    token_path = os.path.join(config_dir, 'token.json')
    credentials_path = os.path.join(config_dir, 'credentials.json')
    
    creds = None
    
    # Load existing token
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to refresh credentials: {str(e)}. Run gdrive_auth.py to re-authenticate.'
                }
        else:
            if not os.path.exists(credentials_path):
                return {
                    'success': False,
                    'error': f'Google Drive credentials not found. Please place credentials.json in {config_dir}'
                }
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Authentication failed: {str(e)}'
                }
        
        # Save token
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': title or os.path.basename(file_path),
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return {
            'success': True,
            'file_id': file.get('id'),
            'url': file.get('webViewLink')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }

def get_config():
    """Load configuration."""
    config_path = os.path.expanduser('~/.openclaw/video-archiver/config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: upload_gdrive.py <file_path> [title]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    config = get_config()
    folder_id = config.get('folder_id')
    
    result = upload_to_drive(file_path, title, folder_id)
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result['success'] else 1)
