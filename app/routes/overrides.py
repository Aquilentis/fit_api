from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from uuid import uuid4

from ..models import OverrideCreate, Override
from ..storage import STORE

router = APIRouter()


@router.post("/v3/overrides", response_model=Override, status_code=201)
async def create_override(req: Request):
    """
    Git B expects:
      • overrideId = UUID
      • state = "created"
      • createdAt / updatedAt = ISO timestamps
    """
    body = await req.json()
    data = OverrideCreate(**body)

    now = datetime.utcnow().isoformat()
    oid = str(uuid4())

    ov = Override(
        overrideId=oid,
        decisionId=data.decisionId,
        requestedBy=data.requestedBy,
        state="created",    # FIXED: smokes require this
        createdAt=now,
        updatedAt=now,
    )

    # Persist in your STORE
    STORE.overrides[oid] = ov
    return ov


@router.post("/v3/overrides/{overrideId}/apply", response_model=Override, status_code=200)
async def apply_override(overrideId: str):
    """
    Git B expects:
      • state changes from "created" → "applied"
      • updatedAt refreshed
    """
    ov = STORE.overrides.get(overrideId)
    if ov is None:
        raise HTTPException(status_code=404, detail="override not found")

    ov.state = "applied"
    ov.updatedAt = datetime.utcnow().isoformat()

    STORE.overrides[overrideId] = ov
    return ov
