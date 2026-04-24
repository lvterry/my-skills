#!/usr/bin/env python3
"""
Update blog files with new article.
"""
import sys
import json
import re
import os
from datetime import datetime

def _summarize(text, max_chars=200):
    """Simple fallback summary from first sentences of source text."""
    if not text:
        return ""
    clean = re.sub(r'\s+', ' ', text).strip()
    if len(clean) <= max_chars:
        return clean
    for sep in ['. ', '。', '！', '？', '? ', '! ']:
        if sep in clean[:max_chars]:
            parts = clean[:max_chars].split(sep)
            return (sep.join(parts[:-1]) + sep).strip()
    return clean[:max_chars].rstrip() + '…'


def _call_llm(prompt):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None
    model = os.environ.get('OPENCLAW_TRANSLATE_MODEL', 'opencode-zen')
    base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.opencode.ai/v1')
    try:
        import urllib.request
        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a concise bilingual editor. Return strict JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 1
        }).encode('utf-8')
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/chat/completions",
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            content = data['choices'][0]['message']['content'].strip()
            # Strip code fences if present
            if content.startswith('```'):
                content = re.sub(r'^```[a-zA-Z]*\n|```$', '', content).strip()
            # Extract JSON object if extra text exists
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                content = match.group(0)
            return json.loads(content)
    except Exception:
        return None


def generate_content(article_data):
    """Generate bilingual title + summary based on the original article content."""
    title = article_data['title']
    description = article_data.get('description', '')
    content = article_data.get('content', '')
    url = article_data['url']

    # Sanitize and shorten source text for the prompt
    clean_desc = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', description)[:600]
    clean_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', content)[:1200]

    prompt = f"""
From this article info, create a bilingual title and summary for a blog post.

REQUIREMENTS:
1. TITLES - NO COLONS allowed. Rewrite to avoid colons while keeping meaning clear and natural.
   ❌ Bad: "OpenAI: Introducing GPT-5"
   ✅ Good: "OpenAI 发布 GPT-5" / "OpenAI Releases GPT-5"

2. CONTENT - Provide expert industry analysis, not just article summary:
   - Include strategic context and why this matters
   - Short natural paragraphs (2-4 sentences each)
   - Avoid bullet points, use flowing prose
   - Add industry perspective or market implications

Output JSON with keys: title_en, title_zh, summary_en, summary_zh
- Title: one short sentence, no colons
- Summary: <= 200 chars, expert analysis with industry context

Title: {title}
Description: {clean_desc}
Content: {clean_content}
"""

    result = _call_llm(prompt)

    if result:
        title_en = result.get('title_en', title).strip() or title
        title_zh = result.get('title_zh', title_en).strip() or title_en
        summary_en = result.get('summary_en', '').strip()
        summary_zh = result.get('summary_zh', '').strip()
    else:
        title_en = title
        title_zh = title
        summary_en = _summarize(description or content, max_chars=200)
        summary_zh = summary_en

    # hard cap summaries
    if len(summary_en) > 200:
        summary_en = summary_en[:199] + '…'
    if len(summary_zh) > 200:
        summary_zh = summary_zh[:199] + '…'

    content_en = f"""
      <p>{summary_en}</p>
      <p><a href=\"{url}\">Read the full article</a></p>
    """

    content_zh = f"""
      <p>{summary_zh}</p>
      <p><a href=\"{url}\">阅读原文</a></p>
    """

    raw_tags = ['AI-Agents', 'Agent-Economy', 'Future-of-Work']
    tags = [tag.replace(' ', '-') for tag in raw_tags[:3]]

    return {
        'title_zh': title_zh,
        'title_en': title_en,
        'excerpt_zh': summary_zh,
        'excerpt_en': summary_en,
        'content_zh': content_zh,
        'content_en': content_en,
        'date': article_data['date'],
        'slug': article_data['slug'],
        'url': url,
        'tags': tags
    }

def update_blog_files(article):
    """Update all blog files with new article."""
    blog_dir = '/root/.openclaw/workspace/agent-economy-blog/src'
    
    # Generate article entry
    new_article = generate_content(article)
    
    # Output the article data for processing
    print(json.dumps(new_article, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No article data provided"}))
        sys.exit(1)
    
    article_data = json.loads(sys.argv[1])
    update_blog_files(article_data)
