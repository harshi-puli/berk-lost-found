import requests
import json
import time
from datetime import datetime
from datetime import timezone

HEADERS = {"User-Agent": "berkeley-lost-found/1.0"}

LOST_KEYWORDS = ["lost", "missing", "anyone seen", "help find", "left behind", "dropped"]
FOUND_KEYWORDS = ["found it", "recovered", "got it back", "returned", "resolved",
                  "already found", "been found", "has been found", "dm me", "dm sent",
                  "claimed", "picked up", "reunited"]

def is_lost_post(title, body):
    text = (title + " " + body).lower()
    return any(kw in text for kw in LOST_KEYWORDS)

def is_resolved(comments):
    for comment in comments:
        if any(kw in comment.lower() for kw in FOUND_KEYWORDS):
            return True
    return False

def get_comments(permalink):
    url = f"https://www.reddit.com{permalink}.json"
    try:
        time.sleep(1)
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return []
        data = res.json()
        comments = []
        if len(data) > 1:
            for item in data[1]["data"]["children"]:
                if item["kind"] == "t1":
                    comments.append(item["data"].get("body", ""))
        return comments
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def scrape_berkeley():
    print("Scraping r/berkeley...")
    url = "https://www.reddit.com/r/berkeley/search.json?q=lost+found&sort=new&limit=50&restrict_sr=true"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            print(f"Error: status {res.status_code}")
            return []
        data = res.json()
    except Exception as e:
        print(f"Scrape failed: {e}")
        return []

    posts = []
    for item in data["data"]["children"]:
        p = item["data"]
        title = p.get("title", "")
        body = p.get("selftext", "")

        if not is_lost_post(title, body):
            continue

        print(f"  Checking: {title[:60]}...")
        comments = get_comments(p["permalink"])
        resolved = is_resolved(comments)

        if resolved:
            print(f"    → Resolved, skipping")
            continue

        posts.append({
            "id": p["id"],
            "title": title,
            "body": body[:500],
            "author": p["author"],
            "url": "https://reddit.com" + p["permalink"],
            "created_utc": p["created_utc"],
            "created_date": datetime.utcfromtimestamp(p["created_utc"]).strftime("%Y-%m-%d %H:%M UTC"),
            "num_comments": p["num_comments"],
            "resolved": False
        })
        time.sleep(0.5)

    print(f"\nFound {len(posts)} active lost items")
    return posts

if __name__ == "__main__":
    posts = scrape_berkeley()
    with open("berkeley_lost.json", "w") as f:
        json.dump({"scraped_at": datetime.now(timezone.utc).isoformat(), "posts": posts}, f, indent=2)
    print("Saved to berkeley_lost.json")