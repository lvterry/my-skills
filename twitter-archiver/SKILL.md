---
name: twitter-archiver
description: Extract and archive Twitter/X content to a local SQLite database. Use when the user sends Twitter/X links and wants to save tweet content (text, author, date, media) for later reference, search, or organization.
---

# Twitter Archiver

Archive tweets from Twitter/X links to a searchable local database.

## Quick Start

1. Send a Twitter/X link to the agent
2. The agent extracts and archives the tweet
3. Search archived tweets with `/search <query>`
4. List recent archives with `/list [count]`

## Database Schema

SQLite database at `~/.openclaw/twitter-archive.db`

Table: `tweets`
- `id` (INTEGER PRIMARY KEY)
- `url` (TEXT UNIQUE) - Original tweet URL
- `tweet_id` (TEXT) - Twitter's tweet ID
- `author` (TEXT) - Tweet author handle
- `content` (TEXT) - Full tweet text
- `created_at` (TEXT) - ISO timestamp
- `archived_at` (TEXT) - When archived
- `media_urls` (TEXT) - JSON array of media URLs
- `tags` (TEXT) - Comma-separated tags

## Usage

### Archive a tweet

Send any Twitter/X link in a message. The agent will:
1. Extract the tweet content
2. Save to database
3. Confirm with a summary

### Search archived tweets

```
/search <keywords>
```

Searches in: author, content, tags

### List recent tweets

```
/list [count]
```

Shows last N archived tweets (default: 10)

### Add tags

```
/tag <tweet-url> <tag1,tag2,...>
```

Add tags to an existing archived tweet.

## Scripts

- `scripts/extract_tweet.py` - Extract tweet content from URL
- `scripts/archive_tweet.py` - Save tweet to database
- `scripts/search_tweets.py` - Search the archive

## Technical Notes

- Uses web scraping (no Twitter API required)
- Falls back to Nitter instances if Twitter blocks scraping
- Media URLs are stored but not downloaded (link to originals)
