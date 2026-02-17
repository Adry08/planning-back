import os
import json
import base64
import requests

API = "https://api.github.com"


def _headers():
    return {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }


def check_github_connection():
    repo = os.getenv("GITHUB_REPO")
    r = requests.get(f"{API}/repos/{repo}", headers=_headers())
    if r.status_code == 200:
        return True, "Connexion GitHub OK"
    return False, "Connexion GitHub échouée"


def commit_json(data: dict):
    repo = os.getenv("GITHUB_REPO")
    branch = os.getenv("GITHUB_BRANCH", "main")
    path = os.getenv("GITHUB_JSON_PATH", "planning_complet.json")

    url = f"{API}/repos/{repo}/contents/{path}"

    r = requests.get(url, headers=_headers())
    sha = r.json().get("sha") if r.status_code == 200 else None

    content = base64.b64encode(
        json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": f"update planning_complet.json – {data.get('annee')} S{data.get('semaine')}",
        "content": content,
        "branch": branch
    }

    if sha:
        payload["sha"] = sha

    res = requests.put(url, headers=_headers(), json=payload)
    res.raise_for_status()