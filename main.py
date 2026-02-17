from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import os

from excel_parser import excel_to_json
from github_client import (
    check_github_connection,
    commit_json
)

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def admin_page():
    with open("templates/admin.html", encoding="utf-8") as f:
        return f.read()


@app.get("/check-github")
def check_github():
    ok, message = check_github_connection()
    return {"ok": ok, "message": message}


@app.post("/preview")
async def preview_excel(
    file: UploadFile = File(...),
    token: str = Form(...)
):
    if token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=401, detail="Token admin invalide")

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Fichier .xlsx requis")

    file_bytes = await file.read()
    data = excel_to_json(file_bytes)
    return JSONResponse(content=data)


@app.post("/publish")
async def publish_excel(
    file: UploadFile = File(...),
    token: str = Form(...)
):
    if token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=401, detail="Token admin invalide")

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Fichier .xlsx requis")

    file_bytes = await file.read()
    data = excel_to_json(file_bytes)

    commit_json(data)

    return {
        "status": "ok",
        "annee": data.get("annee"),
        "semaine": data.get("semaine"),
        "agents": len(data.get("agents", []))
    }