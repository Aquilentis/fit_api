from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Iterable
from .models import Alert

class _Store:
    """
    Minimal in-memory store with both:
      - per-user buckets, and
      - a flat list for date-wide scans.
    """

    def __init__(self) -> None:
        self._alerts: Dict[str, List[Alert]] = defaultdict(list)  # userId -> [Alert]
        self._all_alerts: List[Alert] = []                        # flat list

    # --- ALERTS ---
    def add_alert(self, user_id: str, alert: Alert) -> None:
        self._alerts[user_id].append(alert)
        self._all_alerts.append(alert)

    def get_alerts(self, user_id: str, date: str | None = None) -> List[Alert]:
        lst = list(self._alerts.get(user_id, []))
        if date:
            lst = [a for a in lst if getattr(a, "date", None) == date]
        return lst

    def all_alerts(self) -> Iterable[Alert]:
        return list(self._all_alerts)

# Singleton
STORE = _Store()
