# Plan stage – TaskFlow

## Vision
A lightweight REST API for creating and tracking tasks, delivered through an automated, monitored CI/CD pipeline.

## User stories (MoSCoW)
| ID | Story | Priority | Acceptance criteria |
|---|---|---|---|
| US-01 | As a user I can create a task with a title | Must | `POST /tasks` → 201; empty or >120-char title → 400 |
| US-02 | As a user I can list and filter tasks by done status | Must | `GET /tasks`, `?done=true/false` |
| US-03 | As a user I can view, update and delete a task | Must | 200/204, unknown id → 404 |
| US-04 | As an operator I can check service health | Must | `GET /health` returns status + version + environment |
| US-05 | As a developer, every push is linted, tested and built automatically | Must | Pipeline fails on lint error, failing test or coverage < 90% |
| US-06 | As a developer, passing builds are released as versioned container images | Must | Image tagged `1.0.<build>` in registry |
| US-07 | As an operator, changes deploy to staging then production with an approval gate | Must | Smoke test passes before promotion |
| US-08 | As an operator I can see request rate, errors and latency | Should | Grafana dashboard + Prometheus alerts |
| US-09 | As an operator, a bad release can be rolled back | Should | `kubectl rollout undo` on failure |
| US-10 | As a user my tasks persist in a database | Could | Out of scope (future work) |

## Task breakdown & timeline (adjust dates to your deadline)
| Week | Tasks | Stage |
|---|---|---|
| 1 | Repo + board + branching strategy, write user stories | Plan |
| 1 | Flask API (US-01–04), unit tests | Code / Test |
| 2 | Dockerfile, docker-compose, flake8, coverage gate | Build |
| 2 | CI pipeline (GitHub Actions and/or Jenkins), webhook + cron | Build / Test |
| 3 | Image release to GHCR, k8s manifests, staging + production deploy | Release / Deploy |
| 3 | Prometheus, Grafana, alerts; record 2-minute pipeline video | Operate / Monitor |
| 4 | Write report, collect screenshots, final review | – |

## Branching & workflow
`main` (protected, always deployable) ← `feature/<story-id>-<name>` via pull request; commit messages like `feat(US-02): add done filter`.

## Definition of done
Code reviewed via PR, tests added, pipeline green, deployed to staging, documented.
