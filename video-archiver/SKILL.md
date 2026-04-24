---
name: video-archiver
description: Download videos from YouTube and X (Twitter) links and upload to Google Drive. Use when the user sends video links and wants to save them to cloud storage.
---

# Video Archiver

Download videos from YouTube and X (Twitter) links and save them to Google Drive.

## Quick Start

1. Send a YouTube or X (Twitter) video link
2. Video is automatically downloaded and uploaded to Google Drive
3. Track downloaded videos with `/videos list`
4. Search videos with `/videos search <query>`

## Setup

### Google Drive Authentication

One-time setup required:

```bash
# Run authentication flow
python3 ~/.openclaw/skills/video-archiver/scripts/gdrive_auth.py
```

This will open a browser for Google OAuth authentication. After completion, credentials are saved locally.

## Usage

### Download a video

Send any YouTube or X/Twitter video link:

```
https://www.youtube.com/watch?v=...
https://youtu.be/...
https://twitter.com/.../status/...
https://x.com/.../status/...
```

The agent will:
1. Download the video in best quality
2. Upload to your configured Google Drive folder
3. Save metadata to local database
4. Confirm with video title and Drive link

### List downloaded videos

```
/videos list [count]
```

Shows last N downloaded videos with titles, sources, and Drive links.

### Search videos

```
/videos search <keywords>
```

Searches in: title, source URL, tags

### Add tags to a video

```
/videos tag <video-id> <tag1,tag2,...>
```

## Database Schema

SQLite database at `~/.openclaw/video-archive.db`

Table: `videos`
- `id` (INTEGER PRIMARY KEY)
- `url` (TEXT) - Original video URL
- `title` (TEXT) - Video title
- `source` (TEXT) - 'youtube' or 'twitter'
- `drive_file_id` (TEXT) - Google Drive file ID
- `drive_url` (TEXT) - Google Drive view link
- `local_path` (TEXT) - Local file path (temporary)
- `duration` (INTEGER) - Video duration in seconds (if available)
- `file_size` (INTEGER) - File size in bytes
- `downloaded_at` (TEXT) - ISO timestamp
- `tags` (TEXT) - Comma-separated tags

## Scripts

- `scripts/download_video.py` - Download video from URL
- `scripts/upload_gdrive.py` - Upload to Google Drive
- `scripts/gdrive_auth.py` - Authenticate with Google Drive
- `scripts/video_db.py` - Database operations
- `scripts/video_manager.py` - Main management CLI

## Technical Notes

- Uses `yt-dlp` for downloading (supports 1000+ sites including YouTube, X/Twitter)
- Downloads are temporary and deleted after successful upload
- Google Drive folder ID can be configured in `~/.openclaw/video-archiver/config.json`
- Supports OAuth 2.0 for secure Google Drive access
