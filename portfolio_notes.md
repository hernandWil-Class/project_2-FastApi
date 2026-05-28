# Portfolio Notes

This project demonstrates:

- FastAPI route design
- Pydantic request and response schemas
- Deterministic scoring separated from API handlers
- Configurable thresholds
- Structured JSON logs
- Request IDs
- Unit and API tests
- Dockerized local development
- Documentation for junior engineers

In an interview, explain that a BNPL checkout system would call `/score` before approving an order. The response could decide whether the checkout is accepted immediately, sent to manual review, or rejected.
