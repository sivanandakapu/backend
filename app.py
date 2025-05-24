import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from utils import get_s3_url, search_event_faces

app = FastAPI()

# CORS — allow your frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # on prod, lock this down to your domain
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/spot/{event_id}", response_class=HTMLResponse)
def guest_form(request: Request, event_id: str):
    return templates.TemplateResponse(
        "spot.html", {"request": request, "event_id": event_id}
    )

@app.post("/spot/{event_id}")
async def spot_api(event_id: str, selfie: UploadFile = File(...)):
    """
    Return JSON for your React app instead of HTML.
    """
    img = await selfie.read()
    matched_keys = search_event_faces(img, event_id)
    urls = [get_s3_url(key) for key in matched_keys]
    return JSONResponse({"matches": urls})

@app.get("/health")
def health():
    return {"status": "ok"}
