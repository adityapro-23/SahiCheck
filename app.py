"""app.py – FastAPI server for SahiCheck v2.

Endpoints:
  GET  /api/checks         → static list of 16 checks (id, name, tier, source, max_points)
  GET  /api/demo/{name}    → sample text for 'scam' or 'safe'
  POST /api/check          → multipart form; returns streaming NDJSON

Serving:
  - In development the Vite proxy forwards /api to this server.
  - For a single-command demo, StaticFiles serves frontend/dist when it exists.

CORS is restricted to http://localhost:5173 (Vite dev server) only.
Set CORS_ORIGIN env var to override (e.g. in production).
"""

import io
import json
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from checks_registry import get_checks
from inputs import normalize_input
from pipeline import run as pipeline_run

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")

# CORS origin – only the Vite dev server by default.
CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "http://localhost:5173")

app = FastAPI(title="SahiCheck API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# GET /api/checks
# ---------------------------------------------------------------------------

@app.get("/api/checks")
def list_checks():
    """Returns the 16 checks in order. Frontend renders all rows from this."""
    return get_checks()


# ---------------------------------------------------------------------------
# GET /api/demo/{name}
# ---------------------------------------------------------------------------

_ALLOWED_SAMPLES = {"scam": "demo_scam_fee.txt", "safe": "demo_safe_offer.txt"}


@app.get("/api/demo/{name}")
def get_demo(name: str):
    """Returns sample text. name must be 'scam' or 'safe' (whitelist enforced)."""
    filename = _ALLOWED_SAMPLES.get(name.lower())
    if not filename:
        raise HTTPException(status_code=404, detail="Unknown sample. Use 'scam' or 'safe'.")
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Sample file not found on server.")
    with open(path, "r", encoding="utf-8") as f:
        return {"text": f.read()}


# ---------------------------------------------------------------------------
# POST /api/check  (streaming NDJSON)
# ---------------------------------------------------------------------------

_MAX_TEXT = 5_000          # characters
_MAX_FILE = 10 * 1024 * 1024  # 10 MB
_ALLOWED_TYPES = {"image/png", "image/jpeg", "application/pdf"}
_ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".pdf"}


@app.post("/api/check")
async def check_offer(
    file: Optional[UploadFile] = File(None),
    pasted_text: Optional[str] = Form(None),
    run_web_checks: bool = Form(True),
):
    """
    Accepts multipart/form-data with exactly one of: file or pasted_text.
    Returns application/x-ndjson – one JSON object per line.
    Headers Cache-Control and X-Accel-Buffering prevent proxy buffering.
    """
    # --- Validate inputs ---
    has_file = file is not None and file.filename
    has_text = pasted_text and pasted_text.strip()

    if not has_file and not has_text:
        raise HTTPException(status_code=422, detail="Provide either 'file' or 'pasted_text', not neither.")
    if has_file and has_text:
        raise HTTPException(status_code=422, detail="Provide either 'file' or 'pasted_text', not both.")

    file_bytes: Optional[bytes] = None
    file_suffix: Optional[str] = None

    if has_file:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in _ALLOWED_EXTS:
            raise HTTPException(status_code=422, detail=f"File type '{ext}' not allowed. Use PNG, JPG or PDF.")
        raw = await file.read()
        if len(raw) > _MAX_FILE:
            raise HTTPException(status_code=422, detail="File exceeds 10 MB limit.")
        file_bytes = raw
        file_suffix = ext

    if has_text and len(pasted_text) > _MAX_TEXT:
        raise HTTPException(
            status_code=422,
            detail=f"Text is {len(pasted_text):,} characters; limit is {_MAX_TEXT:,}.",
        )

    # --- Build NormalizedInput in memory (no disk writes) ---
    try:
        if file_bytes is not None:
            norm = normalize_input(
                file_bytes=file_bytes,
                file_suffix=file_suffix,
                pasted_text=None,
            )
        else:
            norm = normalize_input(file_bytes=None, file_suffix=None, pasted_text=pasted_text.strip())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # --- Stream pipeline events ---
    def event_stream():
        """Sync generator; FastAPI runs it in a threadpool."""
        for event in pipeline_run(norm, run_web_checks=run_web_checks):
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Serve built frontend (production single-command demo)
# ---------------------------------------------------------------------------

if os.path.isdir(DIST_DIR):
    # Serve React SPA from /; API routes are registered first so they take priority.
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
