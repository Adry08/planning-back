import os
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH","main")
GITHUB_JSON_PATH = os.getenv("GITHUB_JSON_PATH","planning_complet.json")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

def check_github_connection():
    try:
        repo.get_branch(GITHUB_BRANCH)
        return True, "Connexion repo OK"
    except Exception as e:
        return False, str(e)

def commit_json(data: dict):
    import json
    content = json.dumps(data, ensure_ascii=False, indent=4)
    try:
        file = repo.get_contents(GITHUB_JSON_PATH, ref=GITHUB_BRANCH)
        repo.update_file(GITHUB_JSON_PATH, "Update planning JSON", content, file.sha, branch=GITHUB_BRANCH)
    except:
        repo.create_file(GITHUB_JSON_PATH, "Create planning JSON", content, branch=GITHUB_BRANCH)