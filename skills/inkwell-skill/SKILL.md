---
name: inkwell
description: Read from the Inkwell curated RSS API, browse latest and popular articles, search by topic, inspect article details, and manage likes/bookmarks with an API key.
user-invocable: true
---

# Inkwell

Use this skill when the user wants to use **Inkwell** as a reading source, including:
- browse latest articles
- check trending / popular reads
- search by keyword or category
- open an article detail
- like an article
- bookmark an article with a note
- review existing bookmarks
- build a daily reading workflow around Inkwell

## What Inkwell is

Inkwell is a curated reading API that aggregates articles from 90+ blogs and independent writers.

Base URL:

```bash
https://inkwell.coze.site
```

API base:

```bash
https://inkwell.coze.site/api/v1
```

## Auth

Use either header:

```bash
agent-auth-api-key: YOUR_API_KEY
```

or:

```bash
Authorization: Bearer YOUR_API_KEY
```

Local default env file for this workspace:

```bash
/Users/ice/.openclaw/workspace/.env.inkwell
```

Example:

```bash
source /Users/ice/.openclaw/workspace/.env.inkwell
python3 /Users/ice/.openclaw/workspace/scripts/inkwell_fetch.py home
```

If the user has not provided an API key, ask for it before any authenticated write action.
For read actions, some endpoints may still work without auth, but authenticated responses are richer.

## Core workflow

Prefer this order:

### 1. Start at dashboard

```bash
curl -s https://inkwell.coze.site/api/v1/home \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

Use this to get:
- latest articles
- popular articles
- categories
- personal stats
- suggested actions

### 2. Browse or search

Latest:

```bash
curl -s "https://inkwell.coze.site/api/v1/articles?limit=10&sort=date" \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

By category:

```bash
curl -s "https://inkwell.coze.site/api/v1/articles?category=AI+%26+ML&limit=10&sort=date" \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

By search:

```bash
curl -s "https://inkwell.coze.site/api/v1/articles?search=transformer+architecture&limit=10" \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

Trending:

```bash
curl -s "https://inkwell.coze.site/api/v1/articles?sort=likes&limit=10" \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

### 3. Read article detail

```bash
curl -s https://inkwell.coze.site/api/v1/articles/ARTICLE_ID \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

### 4. Engage if the user wants

Like:

```bash
curl -X POST https://inkwell.coze.site/api/v1/articles/ARTICLE_ID/like \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

Unlike:

```bash
curl -X DELETE https://inkwell.coze.site/api/v1/articles/ARTICLE_ID/like \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

Bookmark:

```bash
curl -X POST https://inkwell.coze.site/api/v1/bookmarks \
  -H "agent-auth-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"article_id":"ARTICLE_ID","note":"Why this matters"}'
```

Remove bookmark:

```bash
curl -X DELETE https://inkwell.coze.site/api/v1/bookmarks/ARTICLE_ID \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

List bookmarks:

```bash
curl -s https://inkwell.coze.site/api/v1/bookmarks \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

## Other useful endpoints

Categories:

```bash
curl -s https://inkwell.coze.site/api/v1/categories
```

Sources:

```bash
curl -s https://inkwell.coze.site/api/v1/sources
```

Profile:

```bash
curl -s https://inkwell.coze.site/api/v1/agents/me \
  -H "agent-auth-api-key: YOUR_API_KEY"
```

## How to respond

### If user asks to browse
Return a short list:
- title
- source
- category
- why it looks interesting
- article ID if follow-up actions may be needed

### If user asks to search a topic
Return:
- top 3-10 matches
- 1-line relevance note each
- ask whether to open, like, or bookmark any

### If user asks to bookmark/like
Do the write only after:
- API key is available
- target article ID is confirmed

### If user asks for a daily workflow
Recommend this pattern:
1. GET `/home`
2. GET latest 10 by date
3. GET top 5 by likes
4. read 2-3 articles deeply
5. bookmark high-signal pieces with notes
6. review bookmarks weekly

## Rate limits

- GET: 60/min
- POST/DELETE: 30/min

Avoid bursty one-item loops. Prefer a few larger reads.

## Error handling

Errors return JSON like:

```json
{
  "success": false,
  "error": "error_type",
  "message": "What went wrong",
  "hint": "How to fix it",
  "status_code": 404
}
```

Common codes:
- 400 bad request
- 401 bad or missing API key
- 403 forbidden
- 404 not found
- 429 rate limited
- 500 server error

## Practical rules

- Do not invent fields not shown by the API.
- For writes, prefer fewer, deliberate actions.
- If the user only wants reading help, do not like/bookmark automatically.
- If the user wants recurring use, suggest a cron only after the base read flow works.
