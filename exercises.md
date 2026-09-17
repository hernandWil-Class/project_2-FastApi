# Exercises

Use this as the practical checklist for `junior_learning_path.md`. The learning
path explains why each task matters; this file tracks what to do.

For slow, step-by-step instructions, use the "How To Do The Exercises Slowly"
section in `junior_learning_path.md`.

## Baseline

- [ ] Run `make help`.
- [ ] Run `make install`.
- [ ] Run `make test`.
- [ ] Run `make run`.
- [ ] Open `/health`, `/docs`, and `/explain`.

## HTTP And FastAPI

- [ ] Trigger `200` with `GET /health`.
- [ ] Trigger `404` with an unknown route.
- [ ] Trigger `405` with `GET /score`.
- [ ] Trigger `422` with invalid request fields.
- [ ] Explain why this project does not currently use `201`, `204`, `401`,
      `403`, `409`, or `503`.
- [ ] Add tests for `404`, `405`, and at least one new `422`.

## File-By-File Micro Exercises

- [ ] `app/__init__.py`: update or explain the package docstring.
- [ ] `app/main.py`: add or test a small route such as `/version`.
- [ ] `app/schemas.py`: add or tighten one validation rule.
- [ ] `app/scoring.py`: add one small scoring rule and reason code.
- [ ] `app/config.py`: add or test one settings behavior.
- [ ] `app/middleware.py`: test generated request IDs.
- [ ] `app/logging_config.py`: inspect JSON logs and explain each field.
- [ ] `tests/conftest.py`: add a reusable high-risk fixture.
- [ ] `tests/test_api.py`: add API status-code tests.
- [ ] `tests/test_scoring.py`: add threshold boundary tests.
- [ ] `tests/test_config.py`: test `.env`, environment, and YAML precedence.
- [ ] `tests/test_integration_httpx.py`: add async batch-score coverage.
- [ ] `config.yaml`: temporarily change thresholds and observe `/explain`.
- [ ] `pyproject.toml`: inspect dependencies and test/lint configuration.
- [ ] `uv.lock`: find locked FastAPI, Pydantic, and Uvicorn versions.
- [ ] `Makefile`: add a useful command such as `smoke` or `test-api`.
- [ ] `Dockerfile`: rebuild the image and explain every instruction.
- [ ] `docker-compose.yml`: modify an environment override and verify it.
- [ ] `.dockerignore`: compare it with `.gitignore`.
- [ ] `.gitignore`: confirm `.env` and generated artifacts are ignored.
- [ ] `README.md`: update examples after API changes.
- [ ] `junior_learning_path.md`: keep notes on what became clear or confusing.
- [ ] `exercises.md`: keep this checklist accurate.
- [ ] `runbook.md`: add a production incident scenario.
- [ ] `tradeoffs.md`: add one architecture or data science tradeoff.
- [ ] `interview_questions.md`: add senior/staff design questions and answers.
- [ ] `portfolio_notes.md`: add one honest production-readiness note.

## Capstone

Add velocity risk scoring with a new `orders_last_24h` request field.

- [ ] Add schema validation and example data.
- [ ] Add deterministic scoring points and reason codes.
- [ ] Update `/explain`.
- [ ] Add unit tests, API tests, config tests if needed, and async integration
      tests.
- [ ] Update README, runbook, tradeoffs, interview questions, portfolio notes,
      and this checklist.
- [ ] Rebuild with Docker Compose.
- [ ] Run `make test` and `make lint`.

The capstone is complete when you can explain every changed file and every test
that protects the new behavior.
