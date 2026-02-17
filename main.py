from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
import os

from excel_parser import excel_to_json
from github_client import commit_json

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def admin_page():
    with open("templates/admin.html", encoding="utf-8") as f:
        return f.read()


@app.post("/upload")
async def upload_excel(
    file: UploadFile = File(...),
    token: str = Form(...)
):
    if token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=401, detail="Token invalide")

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Fichier Excel requis")

    file_bytes = await file.read()
    data = excel_to_json(file_bytes)
    commit_json(data)

    return {
        "status": "ok",
        "annee": data["annee"],
        "semaine": data["semaine"],
        "agents": len(data["agents"])
    }