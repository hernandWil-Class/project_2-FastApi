.PHONY: install run test lint clean docker-build docker-up docker-down

install:
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache .coverage htmlcov dist build *.egg-info .env

docker-build:
	docker build -t fraud-scoring-api .

docker-up:
	docker compose up --build

docker-down:
	docker compose down
