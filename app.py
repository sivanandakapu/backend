# app.py
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from utils import get_s3_url, search_event_faces

app = FastAPI()

# — add CORS here, immediately after creating `app`
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # dev—later lock to your real domain
    allow_methods=["*"],    # GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

@app.post("/spot/{event_id}")
async def spot_api(event_id: str, selfie: UploadFile = File(...)):
    img = await selfie.read()
    matched_keys = search_event_faces(img, event_id)
    urls = [get_s3_url(key) for key in matched_keys]
    return JSONResponse({"matches": urls})

@app.get("/health")
def health():
    return {"status": "ok"}
