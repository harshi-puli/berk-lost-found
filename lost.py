import requests
import json

headers = {"User-Agent": "lost-found-berkeley/1.0"}

url = "https://www.reddit.com/r/berkeley/search.json?q=lost+found&sort=new&limit=25&restrict_sr=true"

##testing out scraping 
response = requests.get(url, headers=headers)
data = response.json()

posts = []
for post in data["data"]["children"]:
    p = post["data"]
    posts.append({
        "title": p["title"],
        "body": p["selftext"],
        "url": "https://reddit.com" + p["permalink"],
        "author": p["author"],
        "time": p["created_utc"]
    })

with open("berkeley_lost.json", "w") as f:
    json.dump(posts, f, indent=2)

print(f"Found {len(posts)} posts")
for p in posts:
    print("-", p["title"])