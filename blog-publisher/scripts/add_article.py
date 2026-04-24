#!/usr/bin/env python3
"""
Add article to blog and publish.
Usage: /add <url> [title]
"""
import sys
import subprocess
import json
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: /add <url> [title]")
        sys.exit(1)
    
    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"📥 Fetching article from {url}...")
    
    # Step 1: Fetch article
    result = subprocess.run(
        ['python3', '/root/.openclaw/skills/blog-publisher/scripts/fetch_article.py', url] + ([title] if title else []),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to fetch article: {result.stderr}")
        sys.exit(1)
    
    article = json.loads(result.stdout)
    print(f"✓ Found: {article['title']}")
    print(f"✓ Date: {article['date']}")
    
    # Step 2: Generate bilingual content
    print("🌐 Generating bilingual content...")
    result = subprocess.run(
        ['python3', '/root/.openclaw/skills/blog-publisher/scripts/generate_content.py', json.dumps(article)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to generate content: {result.stderr}")
        sys.exit(1)
    
    content = json.loads(result.stdout)
    print(f"✓ Generated content for: {content['title_zh']}")
    
    # Output the content for the agent to use
    print("\n" + "="*60)
    print("ARTICLE_DATA:")
    print(json.dumps(content, ensure_ascii=False))
    print("="*60)
    
    print("\n📋 Next steps:")
    print("1. Update src/pages/blog/[slug].astro with new article")
    print("2. Update src/pages/index.astro with new post entry")
    print("3. Update src/pages/blog/index.astro")
    print("4. Commit and push to deploy")

if __name__ == "__main__":
    main()
