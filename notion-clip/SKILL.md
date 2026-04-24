---
name: notion-clip
description: Save tweets and notes directly to Notion as database entries. Use when the user sends Twitter/X links or notes and wants to save them to Notion for long-term storage and organization.
---

# Notion Clip

Save tweets and notes directly to a Notion database.

## How it works

When you send a tweet link or a note:
1. Content is extracted
2. A new entry is created in your Notion database
3. Each entry contains: title, author, date, content, and source link

## Database Structure

Your Notion database should have these properties:
- **Name** (Title) - Entry title
- Created entries will have content blocks with:
  - Author info
  - Date
  - Full content
  - Source link

## Usage

### Test connection
```
/clip test
```

### Clip a tweet manually
```
/clip tweet <url> <author> <content> [date]
```

### Clip a note manually
```
/clip note <content> [source]
```

## Automatic Integration

Once configured, the Twitter Archiver and Notes skills will automatically save to Notion:
- Sending a tweet/X link → Auto-saves to Notion
- Adding a note → Auto-saves to Notion

## Setup

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Create a database (or use an existing one)
3. Share the database with your integration
4. Provide the integration token and database ID

## Scripts

- `scripts/notion_clip.py` - Main Notion clipping script

## Technical Notes

- Requires `requests` library
- Uses Notion API v2022-06-28
- Content is stored as rich text blocks in the page body
- No local SQLite storage - everything goes directly to Notion
