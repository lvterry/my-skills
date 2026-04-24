#!/usr/bin/env python3
"""
Extract tweet content from Twitter/X URLs.
Supports twitter.com and x.com links.
Uses Twitter oEmbed API as primary method, with Nitter fallback.
"""
import sys
import json
import re
import html
import urllib.request
import urllib.error
import urllib.parse

class TweetExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_tweet_id(self, url):
        """Extract tweet ID from URL."""
        patterns = [
            r'twitter\.com/\w+/status/(\d+)',
            r'x\.com/\w+/status/(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def fetch_with_oembed(self, url):
        """Fetch tweet via Twitter oEmbed API."""
        try:
            oembed_url = f"https://publish.twitter.com/oembed?url={urllib.parse.quote(url)}&omit_script=true"
            req = urllib.request.Request(oembed_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return self.parse_oembed(data, url)
        except Exception as e:
            print(f"oEmbed error: {e}", file=sys.stderr)
            return None
    
    def parse_oembed(self, data, original_url):
        """Parse oEmbed response."""
        html_content = data.get('html', '')
        
        # Extract author from author_url or parse HTML
        author = data.get('author_name', '')
        if not author:
            author_match = re.search(r'twitter\.com/(\w+)', data.get('author_url', ''))
            author = author_match.group(1) if author_match else 'unknown'
        
        # Parse HTML to extract clean text
        # The HTML contains a blockquote with the tweet text
        text_match = re.search(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
        if text_match:
            content = text_match.group(1)
            # Clean HTML entities
            content = html.unescape(content)
            # Remove <br> tags and convert to newlines
            content = re.sub(r'<br\s*/?>', '\n', content)
            # Remove remaining HTML tags
            content = re.sub(r'<[^>]+>', '', content)
            content = content.strip()
        else:
            content = ''
        
        # Extract date from HTML - look for the date link at the end
        date_match = re.search(r'<a[^>]*>([^<]+)</a>\s*</blockquote>', html_content)
        created_at = date_match.group(1).strip() if date_match else ''
        
        return {
            'author': author,
            'content': content,
            'created_at': created_at,
            'media_urls': '[]'
        }
    
    def fetch_with_nitter(self, tweet_id):
        """Try to fetch tweet via Nitter instances (fallback)."""
        nitter_instances = [
            'nitter.net',
            'nitter.it',
            'nitter.cz'
        ]
        
        for instance in nitter_instances:
            try:
                url = f"https://{instance}/i/status/{tweet_id}"
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    html_content = response.read().decode('utf-8')
                    tweet = self.parse_nitter_html(html_content)
                    if tweet:
                        return tweet
            except Exception as e:
                continue
        return None
    
    def parse_nitter_html(self, html_content):
        """Parse tweet data from Nitter HTML."""
        text_match = re.search(r'<div class="tweet-content[^"]*"[^>]*>(.*?)</div>', html_content, re.DOTALL)
        if not text_match:
            return None
        
        text = re.sub(r'<[^>]+>', '', text_match.group(1))
        text = html.unescape(text)
        
        author_match = re.search(r'<a class="username"[^>]*>@([^<]+)</a>', html_content)
        author = author_match.group(1) if author_match else 'unknown'
        
        date_match = re.search(r'<span[^>]*class="[^"]*tweet-date[^"]*"[^>]*title="([^"]+)"', html_content)
        created_at = date_match.group(1) if date_match else None
        
        media = re.findall(r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*tweet-media[^"]*"', html_content)
        
        return {
            'author': author,
            'content': text.strip(),
            'created_at': created_at,
            'media_urls': json.dumps(media)
        }
    
    def extract(self, url):
        """Main extraction method."""
        tweet_id = self.extract_tweet_id(url)
        if not tweet_id:
            return None
        
        # Try oEmbed first (most reliable for public tweets)
        tweet = self.fetch_with_oembed(url)
        if tweet:
            tweet['tweet_id'] = tweet_id
            tweet['url'] = url
            return tweet
        
        # Fallback to Nitter
        tweet = self.fetch_with_nitter(tweet_id)
        if tweet:
            tweet['tweet_id'] = tweet_id
            tweet['url'] = url
            return tweet
        
        return None

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No URL provided"}))
        sys.exit(1)
    
    url = sys.argv[1]
    extractor = TweetExtractor()
    result = extractor.extract(url)
    
    if result:
        print(json.dumps(result))
    else:
        print(json.dumps({"error": "Failed to extract tweet"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
