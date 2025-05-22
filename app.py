import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from utils import get_s3_url, search_event_faces

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/spot/{event_id}", response_class=HTMLResponse)
def guest_form(request: Request, event_id: str):
    return templates.TemplateResponse(
        "spot.html", {"request": request, "event_id": event_id}
    )

@app.post("/spot/{event_id}", response_class=HTMLResponse)
async def spot(request: Request, event_id: str, selfie: UploadFile = File(...)):
    img = await selfie.read()
    matched_keys = search_event_faces(img, event_id)
    urls = [get_s3_url(key) for key in matched_keys]
    return templates.TemplateResponse(
        "spot.html",
        {"request": request, "event_id": event_id, "matches": urls},
    )

@app.get("/health")
def health():
    return {"status": "ok"}
