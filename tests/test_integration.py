"""Integration / smoke tests against a RUNNING container.

The pipeline starts the stack with docker compose and sets BASE_URL.
Skipped automatically when BASE_URL is not set (e.g. plain unit-test runs).
"""
import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL")
pytestmark = pytest.mark.skipif(not BASE_URL, reason="BASE_URL not set")


def test_full_task_lifecycle_over_http():
    created = requests.post(f"{BASE_URL}/tasks", json={"title": "smoke"}, timeout=5)
    assert created.status_code == 201
    tid = created.json()["id"]
    assert requests.put(f"{BASE_URL}/tasks/{tid}", json={"done": True}, timeout=5).json()["done"]
    assert requests.delete(f"{BASE_URL}/tasks/{tid}", timeout=5).status_code == 204


def test_metrics_endpoint_is_scrapeable():
    r = requests.get(f"{BASE_URL}/metrics", timeout=5)
    assert r.status_code == 200
    assert "taskflow_http_requests_total" in r.text
