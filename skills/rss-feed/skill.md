---
name: rss-feed
description: RSS/Atom feed monitor and reader. Subscribe to feeds, check updates, and read entries.
emoji: 📰
version: 1.0.0
---

## RSS Feed Monitor

Python-based RSS/Atom feed monitoring tool. Alternative to blogwatcher, no Go required.

## Installation

```bash
pip install feedparser
```

## Usage

### Add a feed
```bash
python3 agent.py '{"action": "add", "url": "https://example.com/feed.xml", "name": "Example Blog", "tags": ["tech"]}'
```

### List all feeds
```bash
python3 agent.py '{"action": "list"}'
```

### Check for updates
```bash
# Check all feeds
python3 agent.py '{"action": "check"}'

# Check specific feed
python3 agent.py '{"action": "check", "url": "https://example.com/feed.xml", "limit": 3}'
```

### Remove a feed
```bash
python3 agent.py '{"action": "remove", "feed_id": "feed_xxx"}'
```

## Storage

- Feed list: `~/.openclaw/config/rss/feeds.json`
- State: `~/.openclaw/config/rss/state.json`
