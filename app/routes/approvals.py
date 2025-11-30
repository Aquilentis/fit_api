from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from ..models import ApprovalRequest
from ..storage import STORE

router = APIRouter()

@router.post("/v3/approval-requests", response_model=ApprovalRequest)
async def create_approval(req: Request):
    body = await req.json()
    now = datetime.utcnow().isoformat()
    ap = ApprovalRequest(
        approvalId="apr_"+now,
        userId=body.get("userId","u_123"),
        decisionId=body.get("decisionId","dec_unknown"),
        actionCategory=body.get("actionCategory","schedule_change"),
        state="pending",
        createdAt=now,
        updatedAt=now,
    )
    STORE.approvals[ap.approvalId] = ap
    return ap

@router.post("/v3/approval-requests/{approvalId}/approve", response_model=ApprovalRequest)
async def approve(approvalId: str):
    ap = STORE.approvals.get(approvalId)
    if not ap:
        raise HTTPException(status_code=404, detail="not found")
    ap.state = "approved"
    ap.updatedAt = datetime.utcnow().isoformat()
    return ap

@router.post("/v3/approval-requests/{approvalId}/reject", response_model=ApprovalRequest)
async def reject(approvalId: str):
    ap = STORE.approvals.get(approvalId)
    if not ap:
        raise HTTPException(status_code=404, detail="not found")
    ap.state = "rejected"
    ap.updatedAt = datetime.utcnow().isoformat()
    return ap
