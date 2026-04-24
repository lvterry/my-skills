#!/usr/bin/env python3
"""
Download videos from YouTube, X (Twitter), and other supported sites.
Uses yt-dlp (supports 1000+ sites).
"""
import subprocess
import json
import os
import sys
import tempfile

def download_video(url, output_dir=None):
    """
    Download video from URL.
    Returns dict with: success, title, file_path, duration, file_size, error
    """
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    # Check if yt-dlp is available
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            'success': False,
            'error': 'yt-dlp not found. Please install: python3 -m pip install yt-dlp'
        }
    
    try:
        # Get video info first
        info_result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', url],
            capture_output=True, text=True, timeout=30
        )
        
        if info_result.returncode != 0:
            return {
                'success': False,
                'error': f'Failed to get video info: {info_result.stderr}'
            }
        
        video_info = json.loads(info_result.stdout)
        title = video_info.get('title', 'Unknown')
        duration = video_info.get('duration')
        
        # Download video (best quality, mp4 format preferred)
        output_template = os.path.join(output_dir, '%(title)s_%(id)s.%(ext)s')
        
        download_result = subprocess.run(
            ['yt-dlp', 
             '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
             '--merge-output-format', 'mp4',
             '-o', output_template,
             '--no-warnings',
             url],
            capture_output=True, text=True, timeout=300
        )
        
        if download_result.returncode != 0:
            return {
                'success': False,
                'error': f'Download failed: {download_result.stderr}'
            }
        
        # Find the downloaded file
        # Extract filename from yt-dlp output
        file_path = None
        for line in download_result.stderr.split('\n'):
            if '[Merger]' in line and 'Merging' in line:
                # Parse merger line
                parts = line.split("'")
                if len(parts) >= 2:
                    file_path = parts[1]
                    break
        
        # Alternative: search for the file
        if not file_path:
            video_id = video_info.get('id', '')
            for f in os.listdir(output_dir):
                if video_id in f and f.endswith(('.mp4', '.mkv', '.webm')):
                    file_path = os.path.join(output_dir, f)
                    break
        
        if not file_path or not os.path.exists(file_path):
            return {
                'success': False,
                'error': 'Could not locate downloaded file'
            }
        
        file_size = os.path.getsize(file_path)
        
        return {
            'success': True,
            'title': title,
            'file_path': file_path,
            'duration': duration,
            'file_size': file_size,
            'video_id': video_info.get('id'),
            'source': get_source_type(url)
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Download timed out (5 minutes max)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

def get_source_type(url):
    """Determine source platform from URL."""
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    else:
        return 'other'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: download_video.py <url>")
        print("Downloads video and returns JSON with file info")
        sys.exit(1)
    
    url = sys.argv[1]
    result = download_video(url)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    sys.exit(0 if result['success'] else 1)
