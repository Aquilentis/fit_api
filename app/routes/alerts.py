from fastapi import APIRouter, Query
from typing import List, Tuple
from ..models import Alert
from ..storage import STORE

router = APIRouter()

def _unique(alerts: List[Alert]) -> List[Alert]:
    seen: set[Tuple[str,str,str,str]] = set()
    out: List[Alert] = []
    for a in alerts:
        key = ((a.title or ""), (a.domain or ""), (a.actionCategory or ""), (a.date or ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    try:
        out.sort(key=lambda x: getattr(x, "createdAt", "") or "")
    except Exception:
        pass
    return out

@router.get("/v1/alerts", response_model=List[Alert])
def get_alerts(
    date: str = Query(..., description="YYYY-MM-DD"),
    userId: str | None = None,  # ignored on purpose
):
    alerts = [a for a in STORE.all_alerts() if getattr(a, "date", None) == date]
    return _unique(alerts)
