run:
	python -m uvicorn app.main:app --reload --port 8000

install:
	python -m pip install --upgrade pip && pip install -r requirements.txt

.PHONY: run venv freeze

# Run the FastAPI server
run:
	@source .venv/Scripts/activate && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Create or refresh the virtual environment and install dependencies
venv:
	@"/c/Users/ellio/AppData/Local/Programs/Python/Python313/python.exe" -m venv .venv && \
	source .venv/Scripts/activate && \
	python -m pip install -U pip setuptools wheel && \
	pip install -r requirements.txt

# Freeze current environment into lockfile
freeze:
	@source .venv/Scripts/activate && \
	pip freeze > requirements-lock.txt && \
	git add requirements-lock.txt && \
	git commit -m "Update lockfile" || true
