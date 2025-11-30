from datetime import datetime
from .models import ActionCategory, Alert
from .storage import STORE

# Map known codes -> (finalMode, confirmationLevel, riskDecision, actionCategory)
def map_code(code: str) -> tuple[str, str, str, ActionCategory]:
    mapping = {
        "STACK_90": ("user_confirm","medium","user_confirm","schedule_change"),
        "CONFLICT_HARD": ("blocked","admin","block","schedule_change"),
        "TRAVEL_INSUF": ("admin_flow","admin","admin_only","schedule_change"),
        "FATIGUE_3D": ("user_confirm","medium","user_confirm","schedule_change"),
        "STIM_LATE": ("user_confirm","medium","user_confirm","supplement_add"),
        "RISK_UNKNOWN": ("admin_flow","admin","admin_only","supplement_add"),
        "BANNED_SUBSTANCE": ("blocked","admin","block","supplement_add"),
        # Explicit injury code we’ve seen
        "CONTRA_ROTATOR_CUFF": ("user_confirm","medium","user_confirm","workout_plan"),
    }
    if code in mapping:
        return mapping[code]
    # Heuristic: any unknown code that smells like injury/replace should be workout_plan
    if any(k in (code or "").upper() for k in ("INJ", "REPLACE", "ROTATOR", "CONTRA", "SHOULDER")):
        return ("user_confirm","medium","user_confirm","workout_plan")
    # Default unknown
    return ("user_confirm","medium","user_confirm","override")

def title_for(code: str, action_category: ActionCategory) -> str | None:
    titles = {
        "STACK_90": "Stacked events confirmed",
        "CONFLICT_HARD": "Hard conflict blocked",
        "TRAVEL_INSUF": "Travel time insufficient — admin approval required",
        "FATIGUE_3D": "High fatigue over 3 days — confirm to proceed",
        "STIM_LATE": "Late stimulant — sleep impact risk",
        "RISK_UNKNOWN": "Unknown supplement — admin approval required",
        "BANNED_SUBSTANCE": "Banned substance blocked",
        "CONTRA_ROTATOR_CUFF": "Contraindicated movement replaced",
    }
    t = titles.get(code)
    if not t and action_category == "workout_plan":
        # Fallback guarantees injury replacement alert title
        t = "Contraindicated movement replaced"
    return t

def domain_for(code: str, action_category: ActionCategory) -> str:
    if action_category == "workout_plan":
        return "injury_risk"
    if code in {"STACK_90","CONFLICT_HARD","TRAVEL_INSUF","FATIGUE_3D"}:
        return "schedule_safety"
    if code in {"STIM_LATE","RISK_UNKNOWN","BANNED_SUBSTANCE"}:
        return "supplement_conflict"
    return "general"

def audience_for(code: str, action_category: ActionCategory) -> str:
    if code in {"TRAVEL_INSUF","RISK_UNKNOWN"}:
        return "household_admin"
    return "user"

def severity_for(code: str, action_category: ActionCategory) -> str:
    if code in {"CONFLICT_HARD","BANNED_SUBSTANCE"}:
        return "critical"
    return "warning"

def make_alert(user_id: str, date: str, code: str, action_category: ActionCategory) -> Alert | None:
    title = title_for(code, action_category)
    if not title:
        return None
    now = datetime.utcnow().isoformat()
    alert = Alert(
        alertId=f"A_{(code or 'unknown')}_{now}",
        userId=user_id,
        audience=audience_for(code, action_category),
        date=date,
        severity=severity_for(code, action_category),
        title=title,
        domain=domain_for(code, action_category),
        actionCategory=action_category,
        status="open" if code not in {"STACK_90","CONTRA_ROTATOR_CUFF"} else "resolved",
        createdAt=now,
        updatedAt=now,
    )
    STORE.add_alert(user_id, alert)
    return alert
