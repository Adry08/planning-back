import base64
import requests
import json
import os

GITHUB_API = "https://api.github.com"

def commit_json(data: dict):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    branch = os.getenv("GITHUB_BRANCH", "main")
    path = os.getenv("GITHUB_JSON_PATH", "planning_complet.json")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"

    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    content = base64.b64encode(
        json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": f"update planning_complet.json – {data.get('annee')} S{data.get('semaine')}",
        "content": content,
        "branch": branch
    }

    if sha:
        payload["sha"] = sha

    res = requests.put(url, headers=headers, json=payload)
    res.raise_for_status()