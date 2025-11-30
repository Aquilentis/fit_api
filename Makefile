.ONESHELL:
.SHELLFLAGS := -o errexit -o pipefail -c
.PHONY: run venv freeze

# Adjust this if you move Python
PY := "/c/Users/ellio/AppData/Local/Programs/Python/Python313/python.exe"

# Start the API and STAY running (exec ties the process to make)
run:
	source .venv/Scripts/activate
	APP_VERSION="$$(git describe --tags --abbrev=0 2>/dev/null || echo dev)" \
	APP_COMMIT="$$(git rev-parse --short HEAD)" \
	exec python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Create/refresh venv and install deps
venv:
	$(PY) -m venv .venv
	source .venv/Scripts/activate
	python -m pip install -U pip setuptools wheel
	pip install -r requirements.txt

# Freeze lockfile
freeze:
	source .venv/Scripts/activate
	pip freeze > requirements-lock.txt
	git add requirements-lock.txt
	- git commit -m "Update lockfile"
