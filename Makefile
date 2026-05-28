.PHONY: install run test lint clean docker-build docker-up docker-down

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev]"

run:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTEST)

lint:
	$(RUFF) check .

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache .ruff_cache .coverage htmlcov dist build *.egg-info .env

docker-build:
	docker build -t fraud-scoring-api .

docker-up:
	docker compose up --build

docker-down:
	docker compose down
