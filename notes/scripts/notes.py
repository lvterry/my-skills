#!/usr/bin/env python3
"""
Notes management - save and retrieve personal notes.
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
    return os.path.join(home, "notes.db")

def init_db():
    """Initialize database with schema."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            tags TEXT,
            source TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_note(content, tags=None, source=None):
    """Add a new note."""
    init_db()
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO notes (content, created_at, updated_at, tags, source)
        VALUES (?, ?, ?, ?, ?)
    ''', (content, now, now, tags or '', source))
    
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    
    return {"success": True, "id": note_id}

def search_notes(query, limit=20):
    """Search notes by content, tags, or source."""
    if not os.path.exists(get_db_path()):
        return {"notes": [], "count": 0}
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_pattern = f"%{query}%"
    
    cursor.execute('''
        SELECT * FROM notes 
        WHERE content LIKE ? OR tags LIKE ? OR source LIKE ?
        ORDER BY updated_at DESC
        LIMIT ?
    ''', (search_pattern, search_pattern, search_pattern, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    notes = [dict(row) for row in rows]
    return {"notes": notes, "count": len(notes)}

def list_notes(limit=10):
    """List most recent notes."""
    if not os.path.exists(get_db_path()):
        return {"notes": [], "count": 0}
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM notes 
        ORDER BY updated_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    notes = [dict(row) for row in rows]
    return {"notes": notes, "count": len(notes)}

def get_note(note_id):
    """Get a specific note by ID."""
    if not os.path.exists(get_db_path()):
        return None
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def update_note(note_id, content=None, tags=None):
    """Update a note."""
    init_db()
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Get existing note
    cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {"success": False, "error": "Note not found"}
    
    now = datetime.now().isoformat()
    
    # Update fields
    new_content = content if content is not None else row[1]
    new_tags = tags if tags is not None else row[4]
    
    cursor.execute('''
        UPDATE notes 
        SET content = ?, updated_at = ?, tags = ?
        WHERE id = ?
    ''', (new_content, now, new_tags, note_id))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "id": note_id}

def add_tags(note_id, new_tags):
    """Add tags to an existing note."""
    init_db()
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Get existing tags
    cursor.execute("SELECT tags FROM notes WHERE id = ?", (note_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return {"success": False, "error": "Note not found"}
    
    existing = result[0] or ""
    existing_tags = set(t.strip() for t in existing.split(',')) if existing else set()
    new_tags_set = set(t.strip() for t in new_tags.split(','))
    all_tags = existing_tags | new_tags_set
    all_tags.discard('')
    
    now = datetime.now().isoformat()
    
    cursor.execute(
        "UPDATE notes SET tags = ?, updated_at = ? WHERE id = ?",
        (','.join(sorted(all_tags)), now, note_id)
    )
    conn.commit()
    conn.close()
    
    return {"success": True, "tags": list(all_tags)}

def delete_note(note_id):
    """Delete a note."""
    init_db()
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        return {"success": False, "error": "Note not found"}
    
    conn.commit()
    conn.close()
    
    return {"success": True}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "No note content provided"}))
            sys.exit(1)
        
        content = sys.argv[2]
        tags = sys.argv[3] if len(sys.argv) > 3 else None
        source = sys.argv[4] if len(sys.argv) > 4 else None
        result = add_note(content, tags, source)
        print(json.dumps(result))
    
    elif action == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        result = search_notes(query, limit)
        print(json.dumps(result))
    
    elif action == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = list_notes(limit)
        print(json.dumps(result))
    
    elif action == "get":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "No note ID provided"}))
            sys.exit(1)
        note_id = int(sys.argv[2])
        result = get_note(note_id)
        if result:
            print(json.dumps({"success": True, "note": result}))
        else:
            print(json.dumps({"error": "Note not found"}))
    
    elif action == "update":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Note ID and content required"}))
            sys.exit(1)
        note_id = int(sys.argv[2])
        content = sys.argv[3]
        tags = sys.argv[4] if len(sys.argv) > 4 else None
        result = update_note(note_id, content, tags)
        print(json.dumps(result))
    
    elif action == "tag":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Note ID and tags required"}))
            sys.exit(1)
        note_id = int(sys.argv[2])
        tags = sys.argv[3]
        result = add_tags(note_id, tags)
        print(json.dumps(result))
    
    elif action == "delete":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "No note ID provided"}))
            sys.exit(1)
        note_id = int(sys.argv[2])
        result = delete_note(note_id)
        print(json.dumps(result))
    
    else:
        print(json.dumps({"error": f"Unknown action: {action}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
