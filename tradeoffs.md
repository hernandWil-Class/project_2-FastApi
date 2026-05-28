# Tradeoffs

## Deterministic Policy vs Machine Learning

This project uses deterministic scoring because it is easy to explain and test. A real company might use ML, but still needs explanations, monitoring, and policy overrides.

## Latency vs Detail

Returning score contributions helps users understand decisions, but bigger responses cost more bandwidth and logging storage.

## Simple Thresholds vs Dynamic Thresholds

Static thresholds are easy to reason about. Dynamic thresholds may improve outcomes but require stronger monitoring and governance.

## Batch Size Limits

`/batch-score` allows up to 100 transactions. This protects latency and memory usage for a learning project.

## 10x or 100x Traffic Risks

At much higher traffic, the service may need autoscaling, stricter timeouts, rate limits, async downstream calls, queueing, caching, and better metrics.
