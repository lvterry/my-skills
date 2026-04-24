#!/usr/bin/env python3
"""
Add article to blog - fetch, translate, and publish.
Usage: python3 add_article.py <url> [title]
"""
import sys
import json
import re
import urllib.request
import urllib.error
import subprocess
from datetime import datetime
from pathlib import Path

def fetch_article(url):
    """Fetch article content from URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return parse_article(html, url)
    except Exception as e:
        return {"error": str(e)}

def parse_article(html, url):
    """Parse article from HTML."""
    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "Untitled"
    title = re.sub(r'\s+', ' ', title)
    
    # Extract meta description
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', html, re.IGNORECASE)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
    description = desc_match.group(1).strip() if desc_match else ""
    
    # Use today's date as article creation date
    date = datetime.now().strftime('%Y-%m-%d')
    
    # Extract main content (simplified - get text from article or main tags)
    content = ""
    content_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL | re.IGNORECASE)
    if not content_match:
        content_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL | re.IGNORECASE)
    if content_match:
        # Strip HTML tags
        content = re.sub(r'<[^>]+>', ' ', content_match.group(1))
        content = re.sub(r'\s+', ' ', content).strip()[:2000]  # Limit length
    
    return {
        "url": url,
        "title": title,
        "description": description,
        "date": date,
        "content": content
    }

def generate_slug(title):
    """Generate URL slug from title."""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:50].strip('-')

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No URL provided"}))
        sys.exit(1)
    
    url = sys.argv[1]
    custom_title = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Fetch article
    article = fetch_article(url)
    if "error" in article:
        print(json.dumps(article))
        sys.exit(1)
    
    # Use custom title if provided
    if custom_title:
        article["title"] = custom_title
    
    # Generate slug
    article["slug"] = generate_slug(article["title"])
    
    print(json.dumps(article, ensure_ascii=False))

if __name__ == "__main__":
    main()
