.PHONY: help install run test lint clean docker-build docker-up docker-down docker-logs docker-ps sudo-docker-up sudo-docker-down sudo-docker-logs sudo-docker-ps

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff

help:
	@echo "Useful commands:"
	@echo "  make install       Create .venv and install Python dependencies"
	@echo "  make run           Start the API locally at http://localhost:8000"
	@echo "  make test          Run the test suite"
	@echo "  make lint          Run Ruff checks"
	@echo "  make docker-up     Build and start the API with Docker Compose"
	@echo "  make docker-down   Stop Docker Compose containers"
	@echo "  make docker-logs   Follow Docker Compose logs"
	@echo "  make docker-ps     Show Docker Compose container status"
	@echo "  make sudo-docker-up Run Docker Compose with sudo if Docker permissions are not set"
	@echo "  make clean         Remove local generated files"

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

docker-logs:
	docker compose logs -f fraud-api

docker-ps:
	docker compose ps

sudo-docker-up:
	sudo docker compose up --build

sudo-docker-down:
	sudo docker compose down

sudo-docker-logs:
	sudo docker compose logs -f fraud-api

sudo-docker-ps:
	sudo docker compose ps
