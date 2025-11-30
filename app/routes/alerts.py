from fastapi import APIRouter, Query
from typing import List, Dict, Tuple
from ..models import Alert
from ..storage import STORE

# --- alerts dedupe helper ---
def _dedupe_alerts_for_date(alerts: List[Dict], qdate: str) -> List[Dict]:
    """
    Keep only alerts matching qdate (ISO YYYY-MM-DD if present on alert), then
    de-duplicate by (title, domain, actionCategory). Stable order preserved.
    If alerts don't carry a 'date' field, we skip the date filter.
    """
    # Filter by date only if alert items actually have a 'date' field
    if alerts and isinstance(alerts[0], dict) and "date" in alerts[0]:
        alerts = [a for a in alerts if a.get("date") == qdate]

    seen: set[Tuple[str, str, str]] = set()
    result: List[Dict] = []
    for a in alerts:
        key = (
            a.get("title", ""),
            a.get("domain", ""),
            a.get("actionCategory", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(a)
    return result
# --- end helper ---


router = APIRouter()


@router.get("/v1/alerts", response_model=List[Alert])
def get_alerts(
    date: str = Query(..., description="YYYY-MM-DD"),
    userId: str | None = None,  # ignored intentionally
):
    # pull raw alert objects for matching date
    raw_alerts = [a for a in STORE.all_alerts() if getattr(a, "date", None) == date]

    # convert to dict for dedupe logic
    alerts_dicts = [a.model_dump() for a in raw_alerts]

    # apply dedupe
    deduped = _dedupe_alerts_for_date(alerts_dicts, date)

    # convert back to Alert objects for response_model
    return [Alert(**a) for a in deduped]
