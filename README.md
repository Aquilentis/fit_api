# Fit API — FastAPI Scaffold (matches smoke_matrix_rc1 harness)
Endpoints:
- POST /v3/risk/evaluate
- POST /v3/overrides
- POST /v3/overrides/{overrideId}/apply
- GET  /v1/alerts?userId=...&date=YYYY-MM-DD
- POST /v3/approval-requests
- POST /v3/approval-requests/{approvalId}/approve
- POST /v3/approval-requests/{approvalId}/reject

Run locally:
```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows Git Bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Point the harness:
```bash
export BASE="http://127.0.0.1:8000"
export AUTH="x"
bash scripts/run_smoke.sh
bash scripts/run_smoke_next5.sh
```
