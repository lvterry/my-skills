#!/usr/bin/env python3
"""
Video Archive Database Manager
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.openclaw/video-archive.db")

def init_db():
    """Initialize the database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            source TEXT,
            drive_file_id TEXT,
            drive_url TEXT,
            local_path TEXT,
            duration INTEGER,
            file_size INTEGER,
            downloaded_at TEXT,
            tags TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_video(url, title, source, drive_file_id, drive_url, local_path, duration=None, file_size=None):
    """Add a new video record."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO videos 
        (url, title, source, drive_file_id, drive_url, local_path, duration, file_size, downloaded_at, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (url, title, source, drive_file_id, drive_url, local_path, duration, file_size, 
          datetime.utcnow().isoformat(), ''))
    
    video_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return video_id

def list_videos(limit=10):
    """List recent videos."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, url, title, source, drive_url, downloaded_at, tags
        FROM videos
        ORDER BY downloaded_at DESC
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def search_videos(query):
    """Search videos by keywords."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    cursor.execute('''
        SELECT id, url, title, source, drive_url, downloaded_at, tags
        FROM videos
        WHERE title LIKE ? OR url LIKE ? OR tags LIKE ?
        ORDER BY downloaded_at DESC
    ''', (search_term, search_term, search_term))
    
    results = cursor.fetchall()
    conn.close()
    return results

def add_tags(video_id, tags):
    """Add tags to a video."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT tags FROM videos WHERE id = ?', (video_id,))
    result = cursor.fetchone()
    
    if result:
        existing_tags = result[0] if result[0] else ''
        existing_set = set(filter(None, existing_tags.split(',')))
        new_set = set(filter(None, tags.split(',')))
        all_tags = ','.join(sorted(existing_set | new_set))
        
        cursor.execute('UPDATE videos SET tags = ? WHERE id = ?', (all_tags, video_id))
        conn.commit()
    
    conn.close()

def get_video_by_url(url):
    """Check if video already exists."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM videos WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: video_db.py <command> [args...]")
        print("Commands: init, add, list, search, tag")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'init':
        init_db()
        print(f"Database initialized at {DB_PATH}")
    
    elif cmd == 'add':
        if len(sys.argv) < 8:
            print("Usage: video_db.py add <url> <title> <source> <drive_file_id> <drive_url> <local_path>")
            sys.exit(1)
        video_id = add_video(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
        print(f"Added video with ID: {video_id}")
    
    elif cmd == 'list':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        videos = list_videos(limit)
        for v in videos:
            print(f"[{v[0]}] {v[2]} ({v[3]}) - {v[5]}")
    
    elif cmd == 'search':
        if len(sys.argv) < 3:
            print("Usage: video_db.py search <query>")
            sys.exit(1)
        videos = search_videos(sys.argv[2])
        for v in videos:
            print(f"[{v[0]}] {v[2]} ({v[3]}) - {v[5]}")
    
    elif cmd == 'tag':
        if len(sys.argv) < 4:
            print("Usage: video_db.py tag <video_id> <tags>")
            sys.exit(1)
        add_tags(int(sys.argv[2]), sys.argv[3])
        print(f"Tags added to video {sys.argv[2]}")
