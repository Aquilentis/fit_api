run:
	python -m uvicorn app.main:app --reload --port 8000

install:
	python -m pip install --upgrade pip && pip install -r requirements.txt
