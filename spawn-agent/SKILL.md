---
name: spawn-agent
description: Auto-spawn subagents using the /spawn command. Use /spawn prefix before any task to automatically delegate it to a background subagent.
---

# Spawn Agent

Automatically delegate tasks to background subagents using the `/spawn` command.

## Usage

Prefix any task with `/spawn` to run it in a background subagent:

```
/spawn search for the latest OpenAI announcements and summarize them
/spawn analyze the codebase and suggest improvements
/spawn fetch content from https://example.com and extract key points
/spawn write a Python script to process CSV files
```

## How it works

1. When you use `/spawn`, the main agent detects this keyword
2. The task is automatically delegated to a subagent
3. The subagent runs independently in a separate session
4. Results are reported back when complete

## Benefits

- **Non-blocking** - Main agent stays responsive
- **Parallel processing** - Multiple subagents can run simultaneously
- **Isolation** - Subagents have fresh context, no pollution
- **Long-running tasks** - Subagents can run for minutes without blocking

## Examples with other skills

### With web search
```
/spawn search for information about Claude 3.7 and create a summary
```

### With blog publisher
```
/spawn fetch https://example.com/article and add it to the blog
```

### With notion-clip
```
/spawn clip this tweet to Notion https://x.com/user/status/123
```

### With course-learning
```
/spawn calculate my Spanish learning statistics for the past month
```

## Combining multiple skills

```
/spawn search for 5 recent AI agent news articles, summarize each, and add them to the blog
```

This will:
1. Search for articles (web search skill)
2. Summarize each (built-in capability)
3. Add to blog (blog-publisher skill)

All in a single subagent call.

## Technical Details

- Subagents run with `sessions_spawn` under the hood
- Default timeout: 10 minutes (600 seconds)
- Subagents inherit allowed tools from parent
- Output is automatically reported back to the main session
- Failed subagents show error messages

## Scripts

- `scripts/spawn.py` - Trigger file (main agent handles actual spawning)

## Note

The `/spawn` keyword is intercepted by the main agent before other processing. Everything after `/spawn` becomes the task description for the subagent.
