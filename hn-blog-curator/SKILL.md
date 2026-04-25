---
name: hn-blog-curator
description: Curate Hacker News top or front-page stories into blog-worthy picks for Agent Economy. Use when the user asks to browse HN top/front page, pick the most relevant items, or summarize which links are worth turning into posts. Prefer direct retrieval plus model judgment; use bundled scripts only as fallback fetch helpers, not as the decision-maker.
---

# HN Blog Curator

Curate Hacker News with editorial judgment, not keyword scoring.

If you need a quick reminder of Agent Economy fit, read `references/blog-focus.md`.

## Default approach

1. Fetch the current HN front page or top stories.
2. Scan titles, domains, score, and comment activity.
3. Shortlist only items that plausibly fit Agent Economy.
4. Open promising links to verify substance before recommending them.
5. Return a tight list of the best picks.

## Editorial lens

Prioritize stories that matter to Agent Economy themes:
- AI infrastructure
- security, trust, verification, provenance
- commercialization, business models, developer economics
- agent workflows, tooling, applications, coordination
- payments, markets, trading, financial rails

Prefer:
- Original research or strong technical writing
- Product launches with real strategic implications
- Infrastructure shifts, protocol changes, platform moves
- New tools that change how builders work
- Essays with clear market or systems insight

Avoid unless the user explicitly wants them:
- Pure memes, flamewars, or shallow hot takes
- Generic startup drama with no lasting insight
- Hiring posts, Show HN projects with little substance, reposts
- Stories whose headline sounds relevant but source page is thin

## Retrieval

Prefer lightweight direct retrieval over dedicated scripts.

### Option A: fetch HN items directly
Use the Hacker News Firebase API to get top story IDs and item metadata.

Example pattern:
```bash
python3 - <<'PY'
import json, urllib.request
base='https://hacker-news.firebaseio.com/v0'
ids=json.load(urllib.request.urlopen(base + '/topstories.json'))[:20]
items=[]
for i in ids:
    item=json.load(urllib.request.urlopen(f'{base}/item/{i}.json'))
    items.append({
        'id': item.get('id'),
        'title': item.get('title'),
        'url': item.get('url'),
        'score': item.get('score'),
        'descendants': item.get('descendants'),
        'by': item.get('by')
    })
print(json.dumps(items, ensure_ascii=False))
PY
```

### Option B: use the bundled fetch helper
Use `scripts/fetch_hn_top.py` only if that is faster or more reliable in the current environment.

Keep scripts limited to retrieval. Do not delegate editorial selection to rigid scoring logic.

## Selection rubric

When choosing stories, weigh:
- **Relevance**: Is it actually connected to Agent Economy themes?
- **Signal**: Is there a real idea, launch, dataset, protocol, or market move here?
- **Originality**: Is it additive versus obvious or repetitive?
- **Blog potential**: Could Terry plausibly turn this into a post with analysis?
- **Source quality**: Does the linked page hold up when inspected?

A high-score HN post is not automatically a good pick.
A low-score post can still be a strong pick if the source is excellent and strategically important.

## Output

Default to a two-tier editorial triage:

**Strong picks**
- Items Terry could realistically turn into worthwhile posts right now.

**Maybe picks**
- Interesting items that are relevant but weaker, thinner, more repetitive, or less clearly aligned.

Default response format:

**Strong picks**
- 标题 — URL — one short reason

**Maybe picks**
- 标题 — URL — one short reason

Guidelines:
- Keep Strong picks short and selective. Usually 2-5 items.
- Add Maybe picks only when they are genuinely useful.
- If nothing is strong, say so plainly instead of padding the list.
- If the user asks for a bare list, omit reasons and keep the same tiering.

## Default reply template

When replying to Terry, prefer a clean editorial format like this:

```markdown
Strong picks
- 标题 — URL — 一句话说明为什么值得写
- 标题 — URL — 一句话说明为什么值得写

Maybe picks
- 标题 — URL — 一句话说明为什么可能值得看
- 标题 — URL — 一句话说明为什么暂时放在次选
```

Style rules:
- Keep reasons short, concrete, and editorial.
- Explain the angle, not just the topic.
- Do not pad the Maybe section if it is weak.
- If there are no strong picks, say so directly and list only Maybe picks when helpful.
- If the user asks for English, switch the labels and reasons to English.

## Notes

- Use your own judgment for ranking and filtering.
- Read source pages for finalists before recommending them.
- If several items cluster around the same story, keep only the strongest one.
- If the user asks for “top 20” or “front page browse,” include more items but still separate strong picks from merely relevant ones.
