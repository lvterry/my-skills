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
4. **Publish** - Git commit and push, Vercel auto-deploys

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
4. **本地构建测试**: 在 push 前必须运行 `npm run build` 确保构建成功
5. Commit and push

### 构建测试要求

**在每次 push 前必须执行：**
```bash
cd /path/to/agent-economy-blog
npm run build
```

**如果构建失败：**
- 修复错误（常见错误：import 路径缺少 `.astro` 扩展名、语法错误等）
- 重新运行 `npm run build` 直到成功
- 然后再 commit 和 push

**构建成功标志：**
- 输出包含 `Complete!` 或 `Generated static` 等成功信息
- 没有 `[ERROR]` 或 `Build failed` 等错误

## Article Page Template (Required Format)

When creating `src/pages/blog/[slug].astro`, **必须使用以下标准模板**（参考现有文章如 `openai-workspace-agents-chatgpt.astro`）：

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
    <!-- 中文标题 -->
    <h1 class="lang-content lang-zh active">中文标题</h1>
    <!-- 英文标题 -->
    <h1 class="lang-content lang-en">English Title</h1>
    
    <time datetime="YYYY-MM-DD">YYYY-MM-DD</time>
    
    <!-- 中文内容 -->
    <div class="lang-content lang-zh active">
      <p>中文段落...</p>
      <p><a href="https://original-url" target="_blank">阅读原文</a></p>
    </div>
    
    <!-- 英文内容 -->
    <div class="lang-content lang-en">
      <p>English paragraph...</p>
      <p><a href="https://original-url" target="_blank">Read the full article</a></p>
    </div>
    
    <a href="/" class="back-link">← Back to articles</a>
  </article>
</Layout>
```

### 模板关键要求：
- **必须**使用 `lang-content lang-zh` 和 `lang-content lang-en` class
- **必须**使用 `active` class 标记默认显示的语言（中文）
- **必须**分开中英文内容到独立的 div 中
- **必须**包含原文链接（中文用"阅读原文"，英文用"Read the full article"）
- **必须**包含返回链接 `<a href="/" class="back-link">`
- **禁止**混合格式（如之前错误的 bilingual div 结构）

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
- **Add value**: Include context about why this matters, industry implications, or strategic significance
- ❌ Bad: Simple restatement of article facts
- ✅ Good: "This move signals OpenAI's shift toward enterprise..." with analysis of market positioning
