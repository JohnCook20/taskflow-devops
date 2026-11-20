# Evidence checklist for the WRIT1 report (take these yourself from your own runs)

The marking criteria reward *evidence of a working pipeline*. Every screenshot must come from **your** real runs, with your GitHub username / timestamps visible.

| Report section | Evidence to capture | File(s) to cite |
|---|---|---|
| Case study overview | Architecture diagram (render `docs/ARCHITECTURE.md`), Postman/curl screenshots of the API, app running | `app/main.py` |
| Plan | GitHub Projects board with user stories; screenshot of issues/milestones | `docs/PLAN.md` |
| Code | IDE (VS Code) screenshot, **your own** commit history (`git log --oneline --graph`), PRs, branches, Dockerfile + compose | `Dockerfile`, `docker-compose.yml` |
| Build | Pipeline run showing Lint + Build Image stages; `docker images` | `Jenkinsfile`, `ci-cd.yml` |
| Test | pytest output with coverage %, JUnit report in Jenkins, a deliberately failing run then fixed run, webhook delivery page, cron schedule | `tests/`, `setup.cfg` |
| Release | Versioned tags in GHCR (`1.0.N`, `latest`) | pipeline *Release* stage |
| Deploy | Staging → approval prompt → production stages; `kubectl get pods -n taskflow-staging / -n taskflow-production`; 2-min screen recording of a full run | `k8s/`, `ansible/` |
| Operate | `kubectl rollout status`, HPA (`kubectl get hpa`), a rollback demo, probes | `k8s/base/` |
| Monitor | Prometheus Targets page (UP), Grafana dashboard under load, a firing alert (stop the app) | `monitoring/` |
| Challenges | Real problems you hit (e.g. webhook reachability, kubeconfig secrets, single-worker in-memory state) and how you fixed them | – |

Tips for top marks: critically *evaluate* choices (Jenkins vs GitHub Actions, Compose vs Kubernetes, rolling vs blue/green), compare with waterfall/manual deployment, and use Harvard-referenced sources (e.g. Kim et al., *The DevOps Handbook*; Humble & Farley, *Continuous Delivery*; Docker/Kubernetes/Prometheus docs).
