---
name: notes
description: Save and manage personal notes in a local SQLite database. Use when the user wants to save text notes, ideas, thoughts, or summaries for later reference, search, or organization.
---

# Notes

Save and retrieve personal notes in a searchable local database.

## Quick Start

1. Add a note: `/note <your note text>`
2. Search notes: `/notes search <keywords>`
3. List recent notes: `/notes list [count]`
4. Add tags: `/notes tag <note-id> <tag1,tag2,...>`

## Database Schema

SQLite database at `~/.openclaw/notes.db`

Table: `notes`
- `id` (INTEGER PRIMARY KEY)
- `content` (TEXT) - The note text
- `created_at` (TEXT) - ISO timestamp
- `updated_at` (TEXT) - ISO timestamp
- `tags` (TEXT) - Comma-separated tags
- `source` (TEXT) - Optional source/reference

## Usage

### Add a note

```
/note Remember to buy groceries: milk, eggs, bread
```

### Search notes

```
/notes search groceries
```

Searches in: content, tags, source

### List recent notes

```
/notes list 5
```

Shows last N notes (default: 10)

### Add tags to a note

```
/notes tag 5 work,urgent
```

### Update a note

```
/notes update 5 Remember to buy groceries: milk, eggs, bread, cheese
```

### Delete a note

```
/notes delete 5
```

## Scripts

- `scripts/notes.py` - Main notes management script

## Technical Notes

- All timestamps stored in UTC
- Search is case-insensitive
- Tags are stored comma-separated and automatically deduplicated
