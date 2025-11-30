from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from ..models import OverrideCreate, Override
from ..storage import STORE

router = APIRouter()

@router.post("/v3/overrides", response_model=Override)
async def create_override(req: Request):
    body = await req.json()
    data = OverrideCreate(**body)
    now = datetime.utcnow().isoformat()
    oid = "ovr_"+now
    ov = Override(
        overrideId=oid,
        decisionId=data.decisionId,
        requestedBy=data.requestedBy,
        state="user_confirmed",
        createdAt=now,
        updatedAt=now,
    )
    STORE.overrides[oid] = ov
    return ov

@router.post("/v3/overrides/{overrideId}/apply", response_model=Override)
async def apply_override(overrideId: str):
    ov = STORE.overrides.get(overrideId)
    if not ov:
        raise HTTPException(status_code=404, detail="not found")
    ov.state = "applied"
    ov.updatedAt = datetime.utcnow().isoformat()
    return ov
