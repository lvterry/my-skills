#!/usr/bin/env python3
"""
Notion Clip - Save tweets and notes to Notion as child pages
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Notion API configuration - 请从环境变量或配置文件读取
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
PARENT_DB_ID = os.environ.get("NOTION_PARENT_DB_ID", "")
NOTION_API_BASE = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def truncate_title(text, max_length=80):
    """Truncate text for use as page title"""
    text = text.replace('\n', ' ').strip()
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def create_notion_page(title, content_blocks):
    """Create a new page in the database"""
    url = f"{NOTION_API_BASE}/pages"
    
    payload = {
        "parent": {"database_id": PARENT_DB_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": title}}
                ]
            }
        },
        "children": content_blocks
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        page_id = response.json()["id"]
        notion_url = f"https://notion.so/{page_id.replace('-', '')}"
        return {"success": True, "page_id": page_id, "url": notion_url}
    else:
        return {"success": False, "error": response.text}

def make_text_block(text, bold=False):
    """Create a paragraph block"""
    if bold:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": text}, "annotations": {"bold": True}}
                ]
            }
        }
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def make_divider():
    """Create a divider block"""
    return {
        "object": "block",
        "type": "divider",
        "divider": {}
    }

def make_link_block(url):
    """Create a link block"""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": url, "link": {"url": url}}}
            ]
        }
    }

def clip_tweet(url, author, content, date_str=""):
    """Clip a tweet to Notion"""
    # Create title from tweet content
    title = truncate_title(content)
    
    # Build content blocks
    blocks = []
    
    # Author info
    if author:
        blocks.append(make_text_block(f"作者：{author}", bold=True))
    
    # Date
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocks.append(make_text_block(f"时间：{date_str}"))
    
    # Divider
    blocks.append(make_divider())
    
    # Content
    blocks.append(make_text_block(content))
    
    # Divider
    blocks.append(make_divider())
    
    # Source URL
    blocks.append(make_text_block("原文链接：", bold=True))
    blocks.append(make_link_block(url))
    
    # Create page
    result = create_notion_page(title, blocks)
    
    if result["success"]:
        print(f"✅ Tweet clipped to Notion: {title}")
        print(f"   URL: {result['url']}")
        return result
    else:
        print(f"❌ Failed to clip tweet: {result['error']}")
        return result

def clip_note(content, source=""):
    """Clip a note to Notion"""
    # Create title from note content
    title = truncate_title(content)
    
    # Build content blocks
    blocks = []
    
    # Date
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocks.append(make_text_block(f"时间：{date_str}"))
    
    # Source if provided
    if source:
        blocks.append(make_text_block(f"来源：{source}", bold=True))
    
    # Divider
    blocks.append(make_divider())
    
    # Content
    blocks.append(make_text_block(content))
    
    # Create page
    result = create_notion_page(title, blocks)
    
    if result["success"]:
        print(f"✅ Note clipped to Notion: {title}")
        print(f"   URL: {result['url']}")
        return result
    else:
        print(f"❌ Failed to clip note: {result['error']}")
        return result

def test_connection():
    """Test Notion API connection"""
    url = f"{NOTION_API_BASE}/databases/{PARENT_DB_ID}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        db_title = response.json().get("title", [{}])[0].get("text", {}).get("content", "Untitled")
        print(f"✅ Connected to Notion database: {db_title}")
        return True
    else:
        print(f"❌ Failed to connect: {response.text}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: notion_clip.py <command> [args...]")
        print("\nCommands:")
        print("  test                          - Test Notion connection")
        print("  tweet <url> <author> <content> [date]  - Clip a tweet")
        print("  note <content> [source]       - Clip a note")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test":
        test_connection()
    
    elif command == "tweet":
        if len(sys.argv) < 5:
            print("Usage: notion_clip.py tweet <url> <author> <content> [date]")
            sys.exit(1)
        url = sys.argv[2]
        author = sys.argv[3]
        content = sys.argv[4]
        date = sys.argv[5] if len(sys.argv) > 5 else ""
        clip_tweet(url, author, content, date)
    
    elif command == "note":
        if len(sys.argv) < 3:
            print("Usage: notion_clip.py note <content> [source]")
            sys.exit(1)
        content = sys.argv[2]
        source = sys.argv[3] if len(sys.argv) > 3 else ""
        clip_note(content, source)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
