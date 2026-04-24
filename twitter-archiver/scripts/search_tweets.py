#!/usr/bin/env python3
"""
Search archived tweets.
"""
import sys
import json
import sqlite3
import os

def get_db_path():
    """Get database path."""
    return os.path.join(os.path.expanduser("~/.openclaw"), "twitter-archive.db")

def search_tweets(query, limit=20):
    """Search tweets by content, author, or tags."""
    if not os.path.exists(get_db_path()):
        return {"tweets": [], "count": 0}
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_pattern = f"%{query}%"
    
    cursor.execute('''
        SELECT * FROM tweets 
        WHERE content LIKE ? OR author LIKE ? OR tags LIKE ?
        ORDER BY archived_at DESC
        LIMIT ?
    ''', (search_pattern, search_pattern, search_pattern, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    tweets = [dict(row) for row in rows]
    return {"tweets": tweets, "count": len(tweets)}

def list_recent(limit=10):
    """List most recent archived tweets."""
    if not os.path.exists(get_db_path()):
        return {"tweets": [], "count": 0}
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM tweets 
        ORDER BY archived_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    tweets = [dict(row) for row in rows]
    return {"tweets": tweets, "count": len(tweets)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        result = search_tweets(query, limit)
        print(json.dumps(result))
    
    elif action == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = list_recent(limit)
        print(json.dumps(result))
    
    else:
        print(json.dumps({"error": f"Unknown action: {action}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
