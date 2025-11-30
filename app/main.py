from fastapi import FastAPI
from .routes import risk, alerts, approvals  # NOTE: overrides router intentionally NOT imported

app = FastAPI(title="Fit API Scaffold")

import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(os.path.join(BASE_DIR, "static", "favicon.ico"))

# favicon (GET already exists above)

from fastapi import Response  # ensure this import is present at the top of the favicon block

@app.head("/favicon.ico", include_in_schema=False)
def favicon_head():
    # Keep HEAD trivial to avoid file/variable errors
    return Response(status_code=200)


# -------- health --------
@app.get("/health")
def health():
    return {"ok": True}

# -------- overrides (file-backed, single source of truth) --------
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict, Literal, Optional
from fastapi import HTTPException, status
import json, os, threading

class OverrideCreateRequest(BaseModel):
    decisionId: str
    requestedBy: str

class OverrideRecord(BaseModel):
    overrideId: str
    decisionId: str
    requestedBy: str
    state: Literal["created", "applied"] = "created"

class OverrideCreateResponse(BaseModel):
    overrideId: str
    state: Literal["created", "applied"] = "created"

_STORE = os.path.join(os.path.dirname(__file__), "overrides_store.json")
_lock = threading.Lock()

def _load() -> Dict[str, dict]:
    if not os.path.exists(_STORE):
        return {}
    try:
        with open(_STORE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(d: Dict[str, dict]) -> None:
    tmp = _STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f)
    os.replace(tmp, _STORE)

@app.post("/v3/overrides", response_model=OverrideCreateResponse, status_code=status.HTTP_201_CREATED)
def create_override(body: OverrideCreateRequest):
    with _lock:
        db = _load()
        oid = str(uuid4())
        rec = OverrideRecord(
            overrideId=oid,
            decisionId=body.decisionId,
            requestedBy=body.requestedBy,
            state="created",
        )
        db[oid] = rec.model_dump()
        _save(db)
    return OverrideCreateResponse(overrideId=oid, state="created")

@app.post("/v3/overrides/{override_id}/apply", status_code=status.HTTP_204_NO_CONTENT)
def apply_override(override_id: str):
    with _lock:
        db = _load()
        rec: Optional[dict] = db.get(override_id)
        if rec is None:
            raise HTTPException(status_code=404, detail="override not found")
        rec["state"] = "applied"
        db[override_id] = rec
        _save(db)
    return
# ----- end overrides implementation -----


# -------- include other routers (no overrides router here) --------
app.include_router(risk.router)
app.include_router(alerts.router)
app.include_router(approvals.router)


