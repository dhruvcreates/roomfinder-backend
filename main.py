# main.py
from flask import Flask
import json
import requests
from datetime import datetime, timedelta
import os
from github import Github

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Room fetcher is alive!"

@app.route("/fetch")
def fetch_and_push():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
    }

    params = {
    "obj_cache_accl": "0",
    "start_dt": "2025-04-22T00:00:00",
    "comptype": "availability",
    "compsubject": "location",
    "page_size": "100",
    "spaces_query_id": "18413,18414,18415,18416,18417,18418",
    "include": "closed blackouts pending related empty",
    "caller": "pro-AvailService.getData"
}

    res = requests.get("https://25live.collegenet.com/25live/data/uc/run/availability/availabilitydata.json",
                       headers=headers, params=params)
    data = res.json()

    output = []
    for room in data.get("subjects", []):
        for item in room.get("items", []):
            start = float(item["start"])
            end = float(item["end"])
            output.append({
                "room": room["itemName"],
                "event": item["itemName"],
                "start": (datetime(2025, 4, 22) + timedelta(hours=start)).strftime("%I:%M %p"),
                "end": (datetime(2025, 4, 22) + timedelta(hours=end)).strftime("%I:%M %p")
            })

    github_token = os.environ["GITHUB_TOKEN"]
    repo_name = "dhruvcreates/dhruvcreates.github.io"
    file_path = "availability.json"

    g = Github(github_token)
    repo = g.get_repo(repo_name)
    contents = repo.get_contents(file_path)
    repo.update_file(contents.path, "Update availability data", json.dumps(output, indent=2), contents.sha)

    return "✅ Data fetched and pushed to GitHub!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
