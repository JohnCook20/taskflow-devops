# Architecture

```mermaid
flowchart LR
  Dev[Developer] -- git push / PR --> GH[(GitHub repo)]
  GH -- webhook --> CI[Jenkins / GitHub Actions]
  Cron[Nightly cron] --> CI
  CI --> L[Lint: flake8] --> U[Unit tests: pytest + coverage]
  U --> B[Docker build] --> I[Integration + smoke tests via docker compose]
  I --> R[(GHCR image 1.0.N)]
  R --> S[Deploy: Staging]
  S --> ST[Staging smoke test]
  ST --> A{Manual approval}
  A --> P[Deploy: Production]
  P --> PT[Prod smoke test / auto rollback]
  S & P -. /metrics .-> PR[Prometheus]
  PR --> G[Grafana dashboards]
  PR --> AL[Alert rules]
```

## Environments
| Env | Runtime | Replicas | Purpose |
|---|---|---|---|
| CI | docker compose on runner | 1 | integration + smoke tests |
| Staging | k8s namespace `taskflow-staging` (or VM via Ansible) | 1 | pre-prod verification |
| Production | k8s namespace `taskflow-production` (or VM via Ansible) | 3 (HPA 2–5) | live service |
