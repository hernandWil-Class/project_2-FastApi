# Interview Questions

Use these after completing the learning path. Strong answers should reference
specific files and concrete API behavior.

## Fundamentals

1. What problem does this FastAPI service solve?
2. What happens when a valid client sends `POST /score`?
3. What does FastAPI provide that plain Python functions do not?
4. What does Pydantic validate in `TransactionRequest`?
5. Why does invalid input return `422` instead of reaching the scoring function?
6. What is the difference between `200`, `404`, `405`, `422`, and `500`?
7. Why do response models matter for API reliability?
8. What is a request ID and why is it returned in both headers and body?

## Implementation

1. Why does scoring logic live in `app/scoring.py` instead of inside
   `app/main.py`?
2. How do `accept_threshold` and `reject_threshold` affect decisions?
3. How does `config.yaml` differ from environment variables?
4. What does `tests/conftest.py` give the test suite?
5. What is the difference between a unit test, API test, and async integration
   test in this repo?
6. Why does Docker Compose define environment variables even though
   `config.yaml` exists?
7. What does the Dockerfile copy into the image, and what is excluded by
   `.dockerignore`?
8. Why should `uv.lock` not be hand-edited?

## Senior And Staff-Level Prompts

1. How would you roll out a new fraud feature without breaking checkout clients?
2. Which schema changes are backward compatible and which are breaking?
3. What metrics would you monitor after changing scoring thresholds?
4. How would you detect that a new rule increased false rejects?
5. How would you compare deterministic scoring with ML model serving for this
   product?
6. What would you add before exposing this API to real external clients?
7. How would you handle authentication, rate limits, client quotas, and abuse?
8. What would change at 10x, 100x, or 1000x traffic?
9. How would you design an A/B test or shadow-mode rollout for a new scoring
   policy?
10. How would you explain this project to a product leader, an ML engineer, and a
    backend engineer differently?

## Capstone Defense

After adding `orders_last_24h` velocity scoring, be ready to answer:

1. Which files changed and why?
2. What status code does invalid velocity input return?
3. How did you test the new feature at each layer?
4. How would you monitor the new reason code in production?
5. What customer experience risk did the new rule introduce?
