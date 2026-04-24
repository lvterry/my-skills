---
name: blog-publisher
description: Automatically add articles to the Agent Economy blog. Fetch content from URLs, generate bilingual titles and content, and publish to the blog.
---

# Blog Publisher

Automatically add articles to the Agent Economy blog.

## Usage

### Add a new article

```
/add <article-url> [optional-title]
```

**Example:**
```
/add https://example.com/ai-agent-article "The Future of AI Agents"
```

### What happens:

1. **Fetch** - Extracts article title, description, date, and content from the URL
2. **Generate** - Creates bilingual (Chinese/English) titles and content
3. **Update** - Adds article to:
   - `src/pages/blog/[slug].astro` - Full article page
   - `src/pages/index.astro` - Homepage listing
   - `src/pages/blog/index.astro` - Articles page
   - `src/pages/rss.xml.js` - RSS feed
4. **Validate** - Run `npm run build`. Make sure it passes. Fix errors if there's any.
5. **Publish** - Git commit and push, Vercel auto-deploys

## Scripts

- `scripts/fetch_article.py` - Extract article data from URL
- `scripts/generate_content.py` - Generate bilingual content
- `scripts/add_article.py` - Main workflow script

## Article Data Format

The script outputs article data in this format:

```json
{
  "title_zh": "中文标题",
  "title_en": "English Title",
  "excerpt_zh": "中文摘要",
  "excerpt_en": "English excerpt",
  "content_zh": "<p>中文内容...</p>",
  "content_en": "<p>English content...</p>",
  "date": "2026-02-09",
  "slug": "article-slug",
  "url": "https://original-url.com",
  "tags": ["AI Agents", "Business"]
}
```

## Manual Steps After Fetch

The agent should:
1. Run the add script
2. Extract the ARTICLE_DATA
3. Update all blog files with the new article
4. Make sure `npm run build` succeed without error
5. Commit and push

## Article Page Template (Required Format)

When creating `src/pages/blog/[slug].astro`, refer to other article pages in the project. Reuse the page structure.

## Content Requirements

When generating article content, follow these guidelines:

### 1. Title Format
- **No colons** in titles. Rewrite to avoid colons while keeping the meaning clear and natural.
- ❌ Bad: "OpenAI: Introducing GPT-5"
- ✅ Good: "OpenAI 发布 GPT-5" / "OpenAI Releases GPT-5"

### 2. Content Quality
- **Expert perspective**: Provide industry analysis and insights, not just article summaries
- **Short paragraphs**: Use brief, natural paragraphs (2-4 sentences each)
- **Avoid bullet points**: Minimize use of lists; prefer flowing prose
- **Add value**: Include context about why this matters, industry implications, or strategic significance. Keep it clean and concise. Guideline is: if you are a busy person who are interested in AI, you'd want to read it.
- **Length**: Article length should be less than 1000 words. Both for English and Chinese.
- ❌ Bad: Simple restatement of article facts
- ✅ Good: "This move signals OpenAI's shift toward enterprise..." with analysis of market positioning
