---
name: blog-publisher
description: Add and publish articles to the Agent Economy blog from a URL. Use when the user sends `/add <url>` or asks to publish an article. Fetch the source page, write bilingual titles/excerpts/article copy in the blog's voice, update the Astro blog files, run a local build, then commit and push.
---

# Blog Publisher

Publish a new Agent Economy article from a URL.

## Default workflow

1. **Fetch the source first.**
   - Prefer `web_fetch` to read the full article.
   - Optionally run `scripts/fetch_article.py` to extract title, date, and URL metadata.
   - If one source is incomplete, cross-check with the other.

2. **Write the final copy yourself.**
   - Do **not** rely on `scripts/generate_content.py` or `scripts/add_article.py` for final titles, excerpts, or article body.
   - Treat script output as a rough draft at most.
   - The skill should produce the final editorial copy directly.

3. **Update the blog source files.**
   - Create `src/pages/blog/<slug>.astro`
   - Add the post entry to `src/data/posts.ts`
   - Add the RSS entry to `src/pages/rss.xml.js`

4. **Build before publishing.**
   - Run `npm run build` in the blog repo.
   - If build fails, fix the errors and rerun until it passes.

5. **Commit only intended source changes and push.**
   - Avoid including unrelated `dist/`, `test-results/`, or other dirty files.

## Repo and files

- Blog repo: `/root/.openclaw/workspace/agent-economy-blog`
- Source page template reference: existing files in `src/pages/blog/`
- Post list: `src/data/posts.ts`
- RSS feed: `src/pages/rss.xml.js`

## Optional scripts

- `scripts/fetch_article.py`: optional helper for basic metadata extraction
- `scripts/generate_content.py`: draft-only helper; do not trust as final copy
- `scripts/add_article.py`: draft-only helper; do not rely on it for the final workflow

## Editorial rules

### Titles

- Rewrite titles to fit Agent Economy style.
- **Do not use colons** in final Chinese or English titles.
- Keep titles natural, specific, and readable.
- Avoid mechanical translation of the source headline.

### Excerpts

- Write fresh Chinese and English excerpts.
- Keep them to 1-2 sentences.
- Summarize both the fact and why it matters.
- Do not copy the source deck verbatim.

### Article body

- Write from an informed editorial perspective, not as a raw summary.
- Add context, implications, or strategy when useful.
- Prefer short paragraphs.
- Usually avoid bullet lists unless the source is highly technical and a short list genuinely improves clarity.
- Keep the piece concise and worth reading for a busy AI-native audience.

### Voice

- Match Agent Economy themes: AI infrastructure, security, trust, commercialization, applications, and trading.
- Optimize for signal over fluff.
- The article should feel curated, not auto-generated.

## Page template requirements

When creating `src/pages/blog/<slug>.astro`, follow the established article pattern used by existing posts.

Required structure:

```astro
---
import Layout from '../../layouts/Layout.astro';

const title = '中文标题';
const description = '中文描述';
---

<Layout 
  title={title}
  description={description}
  type="article"
  publishedTime="YYYY-MM-DD"
  tags={["Tag1", "Tag2"]}
>
  <article class="article-content">
    <h1 class="lang-content lang-zh active">中文标题</h1>
    <h1 class="lang-content lang-en">English Title</h1>

    <time datetime="YYYY-MM-DD">YYYY-MM-DD</time>

    <div class="lang-content lang-zh active">
      <p>中文段落...</p>
      <p><a href="https://original-url" target="_blank">阅读原文</a></p>
    </div>

    <div class="lang-content lang-en">
      <p>English paragraph...</p>
      <p><a href="https://original-url" target="_blank">Read the full article</a></p>
    </div>

    <a href="/" class="back-link">← Back to articles</a>
  </article>
</Layout>
```

Non-negotiable details:

- Use `lang-content lang-zh` and `lang-content lang-en`
- Use `active` on the default Chinese content
- Keep Chinese and English content in separate blocks
- Include the original source link in both languages
- Include the back link

## Quality bar

Before pushing, check:

- The title does not use a colon
- The excerpt is rewritten, not copied
- The article adds analysis instead of only paraphrasing
- The slug, page, post list, and RSS entry all match
- `npm run build` passes
- The commit contains only the intended article changes
