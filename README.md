# TaskFlow – DevOps case study (DAT6005 WRIT1)

A small task-tracking REST API (Python / Flask) built to demonstrate the **full DevOps lifecycle**:
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor.

| Stage | Where it lives |
|---|---|
| Plan | `docs/PLAN.md` (user stories, tasks, timeline) – mirror it in a GitHub Projects board |
| Code | `app/`, Git + GitHub, Docker config (`Dockerfile`, `docker-compose.yml`) |
| Build | `Dockerfile` (multi-stage), pipeline *Build Image* stage |
| Test | `tests/` – pytest unit + integration, flake8 lint, 90% coverage gate, smoke tests |
| Release | Versioned images (`1.0.<build>`) pushed to GHCR by the pipeline |
| Deploy | `k8s/` (staging + production overlays), `ansible/` (VM alternative), manual approval gate |
| Operate | k8s probes, rolling updates, HPA autoscaling, `rollout undo` on failure |
| Monitor | `/metrics` → Prometheus (`monitoring/`) → Grafana dashboard + alert rules |

Two equivalent pipelines are provided: **`Jenkinsfile`** and **`.github/workflows/ci-cd.yml`**.

## Run it locally (5 minutes)
```bash
python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
flake8 app tests && pytest tests/test_api.py           # lint + unit tests + coverage

APP_VERSION=1.0.0 docker compose up -d --build         # app + Prometheus + Grafana
scripts/smoke_test.sh http://localhost:5000 1.0.0
```
- API: http://localhost:5000/tasks · health: `/health` · metrics: `/metrics`
- Prometheus: http://localhost:9090 (Status → Targets) · Grafana: http://localhost:3000 (admin/admin) → *TaskFlow Overview*
- Generate traffic for the dashboard: `for i in $(seq 1 200); do curl -s -XPOST localhost:5000/tasks -H 'Content-Type: application/json' -d '{"title":"t"}' >/dev/null; done`

## Set up the pipeline

### Option A – GitHub Actions (fastest; no server needed)
1. Create a GitHub repo, push this project to `main`.
2. Edit `YOUR_GITHUB_USER` in `k8s/base/deployment.yaml`.
3. Push. **Test → Build → Integration test → Push image to GHCR** runs automatically (also nightly via cron).
4. For the deploy jobs: Settings → Variables add `DEPLOY_ENABLED=true`, `STAGING_URL`, `PROD_URL`; Environments `staging` and `production` (add *Required reviewers* on production for the approval gate); Secrets `KUBECONFIG_STAGING`, `KUBECONFIG_PRODUCTION` (base64 of each kubeconfig).

### Option B – Jenkins
1. `docker run -d -p 8080:8080 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts` (install Docker CLI + kubectl in it, or use a VM agent).
2. Plugins: Pipeline, Docker Pipeline, GitHub, JUnit, Credentials Binding.
3. Credentials: `ghcr-credentials` (username + token), `kubeconfig-staging`, `kubeconfig-production` (secret files).
4. New Item → *Multibranch Pipeline* → your repo. Edit the `environment {}` block in the `Jenkinsfile`.
5. GitHub repo → Settings → Webhooks → `http://<jenkins-host>/github-webhook/` (needs a public URL, e.g. ngrok, for local Jenkins).

### Staging / production targets
- **Kubernetes:** two clusters or two namespaces on one cluster (`taskflow-staging`, `taskflow-production`). Cheap options: k3s on a cloud VM, minikube, or a managed cluster.
- **Ansible (no Kubernetes):** fill `ansible/inventory.ini`, then
  `ansible-playbook -i ansible/inventory.ini ansible/deploy.yml -l staging -e image=ghcr.io/USER/taskflow:1.0.1 -e app_version=1.0.1`

## Notes
- Task data is held in memory (kept deliberately simple so the focus stays on DevOps); the container runs a single gunicorn worker for that reason.
- Replace every `YOUR_…` placeholder before running.
- Declare any AI assistance in line with Cardiff Met's academic-misconduct / AI guidance.
