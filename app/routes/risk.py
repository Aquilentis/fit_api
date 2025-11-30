from fastapi import APIRouter, Request
from datetime import datetime
from ..models import EvaluateRequest, Decision
from ..logic import map_code, make_alert

router = APIRouter()

@router.post("/v3/risk/evaluate", response_model=Decision)
async def evaluate(req: Request):
    body = await req.json()
    data = EvaluateRequest(**body)
    code = (data.flags or [])[0].code if data.flags else ""
    fm, cl, rd, ac = map_code(code)  # initial guess

    # --- Heuristic promotion for injury/replace codes ---
    U = (code or "").upper()
    looks_injury = any(k in U for k in ("INJ", "REPLACE", "ROTATOR", "CONTRA", "SHOULDER"))
    if ac == "override" and (data.actionCategory == "workout_plan" or looks_injury):
        ac = "workout_plan"
    # ----------------------------------------------------

    now = datetime.utcnow().isoformat()

    # Create alert using the FINAL action category
    make_alert(
        user_id=data.actorUserId,
        date=now[:10],
        code=code,
        action_category=ac
    )

    return Decision(
        decisionId="dec_" + now,
        finalMode=fm,
        confirmationLevel=cl,
        riskDecision=rd,
        actionCategory=ac,
        actorRole="adult",
        flags=[{"id": f.id} for f in data.flags],
        issuedAt=now,
        reason="computed"
    )
