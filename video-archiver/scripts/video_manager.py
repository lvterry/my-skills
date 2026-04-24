#!/usr/bin/env python3
"""
Video Archive Manager - Main CLI
"""
import sys
import os
import json

# Add scripts directory to path
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

def archive_video(url):
    """Download and archive a video to Google Drive."""
    import video_db
    import download_video
    import upload_gdrive
    
    # Check if already archived
    if video_db.get_video_by_url(url):
        print(f"⚠️ Video already archived: {url}")
        return
    
    print(f"📥 Downloading video from: {url}")
    
    # Download
    download_result = download_video.download_video(url)
    
    if not download_result['success']:
        print(f"❌ Download failed: {download_result.get('error', 'Unknown error')}")
        return
    
    print(f"✅ Downloaded: {download_result['title']}")
    print(f"   File: {download_result['file_path']}")
    print(f"   Size: {download_result.get('file_size', 0) / 1024 / 1024:.1f} MB")
    
    # Upload to Google Drive
    print(f"☁️ Uploading to Google Drive...")
    
    upload_result = upload_gdrive.upload_to_drive(
        download_result['file_path'],
        download_result['title']
    )
    
    if not upload_result['success']:
        print(f"❌ Upload failed: {upload_result.get('error', 'Unknown error')}")
        # Keep the file for retry
        return
    
    print(f"✅ Uploaded to Google Drive: {upload_result['url']}")
    
    # Save to database
    video_id = video_db.add_video(
        url=url,
        title=download_result['title'],
        source=download_result['source'],
        drive_file_id=upload_result['file_id'],
        drive_url=upload_result['url'],
        local_path=download_result['file_path'],
        duration=download_result.get('duration'),
        file_size=download_result.get('file_size')
    )
    
    print(f"✅ Saved to database (ID: {video_id})")
    
    # Clean up local file
    try:
        os.remove(download_result['file_path'])
        print(f"🗑️ Cleaned up local file")
    except Exception as e:
        print(f"⚠️ Could not delete local file: {e}")
    
    return {
        'id': video_id,
        'title': download_result['title'],
        'drive_url': upload_result['url']
    }

def list_videos(count=10):
    """List recent videos."""
    import video_db
    
    videos = video_db.list_videos(count)
    
    if not videos:
        print("No videos archived yet.")
        return
    
    print(f"\n📹 Last {len(videos)} archived videos:\n")
    
    for v in videos:
        video_id, url, title, source, drive_url, downloaded_at, tags = v
        print(f"[{video_id}] {title}")
        print(f"    Source: {source}")
        print(f"    Drive: {drive_url}")
        print(f"    Downloaded: {downloaded_at}")
        if tags:
            print(f"    Tags: {tags}")
        print()

def search_videos(query):
    """Search videos."""
    import video_db
    
    videos = video_db.search_videos(query)
    
    if not videos:
        print(f"No videos found for: {query}")
        return
    
    print(f"\n🔍 Found {len(videos)} videos:\n")
    
    for v in videos:
        video_id, url, title, source, drive_url, downloaded_at, tags = v
        print(f"[{video_id}] {title}")
        print(f"    Drive: {drive_url}")
        print()

def tag_video(video_id, tags):
    """Add tags to a video."""
    import video_db
    
    video_db.add_tags(video_id, tags)
    print(f"✅ Tags added to video {video_id}")

def main():
    if len(sys.argv) < 2:
        print("Video Archive Manager")
        print("")
        print("Usage:")
        print("  video_manager.py archive <url>     - Download and archive video")
        print("  video_manager.py list [count]      - List recent videos")
        print("  video_manager.py search <query>    - Search videos")
        print("  video_manager.py tag <id> <tags>   - Add tags to video")
        print("")
        print("Examples:")
        print("  video_manager.py archive 'https://youtube.com/watch?v=...'")
        print("  video_manager.py list 5")
        print("  video_manager.py search 'tutorial'")
        print("  video_manager.py tag 1 'important,work'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'archive':
        if len(sys.argv) < 3:
            print("Usage: video_manager.py archive <url>")
            sys.exit(1)
        result = archive_video(sys.argv[2])
        if result:
            print(f"\n🎉 Successfully archived: {result['title']}")
            print(f"   Google Drive: {result['drive_url']}")
    
    elif command == 'list':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_videos(count)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("Usage: video_manager.py search <query>")
            sys.exit(1)
        search_videos(sys.argv[2])
    
    elif command == 'tag':
        if len(sys.argv) < 4:
            print("Usage: video_manager.py tag <video_id> <tags>")
            sys.exit(1)
        tag_video(int(sys.argv[2]), sys.argv[3])
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
