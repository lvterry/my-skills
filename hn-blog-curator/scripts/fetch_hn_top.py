#!/usr/bin/env python3
#!/usr/bin/env python3
import json
import sys
import time
from urllib.request import urlopen

HN_API = "https://hacker-news.firebaseio.com/v0"


def fetch_json(url):
    with urlopen(url) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_stories(limit=20, story_type="top"):
    endpoint = "topstories" if story_type == "top" else "beststories"
    ids = fetch_json(f"{HN_API}/{endpoint}.json")
    out = []
    for _id in ids[:limit]:
        item = fetch_json(f"{HN_API}/item/{_id}.json")
        if not item:
            continue
        out.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "url": item.get("url"),
            "score": item.get("score"),
            "comments": item.get("descendants"),
            "by": item.get("by"),
            "time": item.get("time"),
            "type": item.get("type"),
        })
        time.sleep(0.05)
    return out


def main():
    limit = 20
    story_type = "top"

    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except Exception:
            pass

    if len(sys.argv) > 2 and sys.argv[2] in {"top", "best"}:
        story_type = sys.argv[2]

    print(json.dumps(fetch_stories(limit, story_type), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
