"""TaskFlow - a small task-tracking REST API used as the DevOps case study."""
import logging
import os
import time
import uuid

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (CONTENT_TYPE_LATEST, CollectorRegistry, Counter,
                               Gauge, Histogram, generate_latest)

VERSION = os.getenv("APP_VERSION", "dev")
ENVIRONMENT = os.getenv("APP_ENV", "local")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
log = logging.getLogger("taskflow")


def create_app():
    app = Flask(__name__)
    app.config["TASKS"] = {}

    registry = CollectorRegistry()
    requests_total = Counter("taskflow_http_requests_total", "HTTP requests",
                             ["method", "endpoint", "status"], registry=registry)
    latency = Histogram("taskflow_http_request_duration_seconds",
                        "Request latency", ["endpoint"], registry=registry)
    tasks_gauge = Gauge("taskflow_tasks_total", "Tasks currently stored",
                        registry=registry)
    info = Gauge("taskflow_build_info", "Build information",
                 ["version", "environment"], registry=registry)
    info.labels(VERSION, ENVIRONMENT).set(1)

    @app.before_request
    def start_timer():
        g.start = time.perf_counter()

    @app.after_request
    def record(resp):
        endpoint = request.url_rule.rule if request.url_rule else "unmatched"
        requests_total.labels(request.method, endpoint, resp.status_code).inc()
        latency.labels(endpoint).observe(time.perf_counter() - g.start)
        tasks_gauge.set(len(app.config["TASKS"]))
        return resp

    @app.get("/health")
    def health():
        return jsonify(status="ok", version=VERSION, environment=ENVIRONMENT)

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

    @app.get("/tasks")
    def list_tasks():
        done = request.args.get("done")
        tasks = list(app.config["TASKS"].values())
        if done is not None:
            wanted = done.lower() == "true"
            tasks = [t for t in tasks if t["done"] == wanted]
        return jsonify(tasks)

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = str(data.get("title", "")).strip()
        if not title:
            return jsonify(error="title is required"), 400
        if len(title) > 120:
            return jsonify(error="title must be 120 characters or fewer"), 400
        task = {"id": str(uuid.uuid4()), "title": title, "done": False}
        app.config["TASKS"][task["id"]] = task
        log.info("task created id=%s", task["id"])
        return jsonify(task), 201

    @app.get("/tasks/<task_id>")
    def get_task(task_id):
        task = app.config["TASKS"].get(task_id)
        if task is None:
            return jsonify(error="task not found"), 404
        return jsonify(task)

    @app.put("/tasks/<task_id>")
    def update_task(task_id):
        task = app.config["TASKS"].get(task_id)
        if task is None:
            return jsonify(error="task not found"), 404
        data = request.get_json(silent=True) or {}
        if "title" in data:
            title = str(data["title"]).strip()
            if not title:
                return jsonify(error="title cannot be empty"), 400
            task["title"] = title
        if "done" in data:
            task["done"] = bool(data["done"])
        return jsonify(task)

    @app.delete("/tasks/<task_id>")
    def delete_task(task_id):
        if app.config["TASKS"].pop(task_id, None) is None:
            return jsonify(error="task not found"), 404
        return "", 204

    return app


app = create_app()
