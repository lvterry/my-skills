#!/usr/bin/env python3
"""
Archive tweet to SQLite database.
"""
import sys
import json
import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Get database path."""
    home = os.path.expanduser("~/.openclaw")
    os.makedirs(home, exist_ok=True)
    return os.path.join(home, "twitter-archive.db")

def init_db():
    """Initialize database with schema."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            tweet_id TEXT NOT NULL,
            author TEXT,
            content TEXT,
            created_at TEXT,
            archived_at TEXT DEFAULT CURRENT_TIMESTAMP,
            media_urls TEXT,
            tags TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def archive_tweet(tweet_data):
    """Save tweet to database."""
    init_db()
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO tweets 
            (url, tweet_id, author, content, created_at, media_urls, archived_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            tweet_data['url'],
            tweet_data['tweet_id'],
            tweet_data.get('author', ''),
            tweet_data.get('content', ''),
            tweet_data.get('created_at', ''),
            tweet_data.get('media_urls', '[]'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        tweet_db_id = cursor.lastrowid
        conn.close()
        
        return {"success": True, "id": tweet_db_id}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}

def add_tags(url, tags):
    """Add tags to an existing tweet."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Get existing tags
    cursor.execute("SELECT tags FROM tweets WHERE url = ?", (url,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return {"success": False, "error": "Tweet not found"}
    
    existing = result[0] or ""
    existing_tags = set(existing.split(',')) if existing else set()
    new_tags = set(tags.split(','))
    all_tags = existing_tags | new_tags
    all_tags.discard('')
    
    cursor.execute(
        "UPDATE tweets SET tags = ? WHERE url = ?",
        (','.join(sorted(all_tags)), url)
    )
    conn.commit()
    conn.close()
    
    return {"success": True, "tags": list(all_tags)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "archive":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "No tweet data provided"}))
            sys.exit(1)
        
        tweet_data = json.loads(sys.argv[2])
        result = archive_tweet(tweet_data)
        print(json.dumps(result))
    
    elif action == "tag":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "URL and tags required"}))
            sys.exit(1)
        
        url = sys.argv[2]
        tags = sys.argv[3]
        result = add_tags(url, tags)
        print(json.dumps(result))
    
    else:
        print(json.dumps({"error": f"Unknown action: {action}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
