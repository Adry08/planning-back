import os
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from excel_parser import excel_to_json
from github_client import check_github_connection, commit_json

app = FastAPI()

# ----------------------------------------------------
# ENV
# ----------------------------------------------------
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
if not ADMIN_TOKEN:
    raise Exception("⚠️ ADMIN_TOKEN non défini dans les variables Render")

# ----------------------------------------------------
# UTIL
# ----------------------------------------------------
def check_admin(x_admin_token: str = Header(None)):
    if not x_admin_token or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Admin token invalide")

# ----------------------------------------------------
# PAGE PRINCIPALE (ADMIN DIRECT)
# ----------------------------------------------------
@app.get("/")
def home():
    return FileResponse("templates/admin.html")

# ----------------------------------------------------
# ROUTE ADMIN (optionnel)
# ----------------------------------------------------
@app.get("/admin")
def get_admin():
    return FileResponse("templates/admin.html")

# ----------------------------------------------------
# ENDPOINTS API
# ----------------------------------------------------
@app.get("/health/github")
def health_github(x_admin_token: str = Header(None)):
    check_admin(x_admin_token)
    ok, message = check_github_connection()
    if ok:
        return {"status": "ok", "message": message}
    else:
        return {"status": "error", "error": message}

@app.post("/upload")
async def upload_excel(
    file: UploadFile = File(...),
    x_admin_token: str = Header(None)
):
    check_admin(x_admin_token)

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Fichier Excel requis")

    file_bytes = await file.read()
    data = excel_to_json(file_bytes)
    return JSONResponse(content={"status": "ok", "json": data})

@app.post("/push")
async def push_json(
    json_data: dict,
    x_admin_token: str = Header(None)
):
    check_admin(x_admin_token)

    try:
        commit_json(json_data)
        return {"status": "ok", "message": "JSON pushé sur GitHub ✔️"}
    except Exception as e:
        return {"status": "error", "error": str(e)}