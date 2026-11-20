"""Unit tests for the TaskFlow API (run by the pipeline's Test stage)."""
import pytest

from app.main import create_app


@pytest.fixture()
def client():
    return create_app().test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_create_and_get_task(client):
    r = client.post("/tasks", json={"title": "Write report"})
    assert r.status_code == 201
    task = r.get_json()
    assert task["done"] is False
    assert client.get(f"/tasks/{task['id']}").get_json()["title"] == "Write report"


@pytest.mark.parametrize("payload", [{}, {"title": ""}, {"title": "   "}, {"title": "x" * 121}])
def test_create_rejects_invalid_titles(client, payload):
    assert client.post("/tasks", json=payload).status_code == 400


def test_create_rejects_non_json(client):
    assert client.post("/tasks", data="nope").status_code == 400


def test_list_and_filter(client):
    a = client.post("/tasks", json={"title": "a"}).get_json()
    client.post("/tasks", json={"title": "b"})
    client.put(f"/tasks/{a['id']}", json={"done": True})
    assert len(client.get("/tasks").get_json()) == 2
    assert len(client.get("/tasks?done=true").get_json()) == 1
    assert len(client.get("/tasks?done=false").get_json()) == 1


def test_update_task(client):
    t = client.post("/tasks", json={"title": "old"}).get_json()
    r = client.put(f"/tasks/{t['id']}", json={"title": "new", "done": True})
    assert r.get_json() == {"id": t["id"], "title": "new", "done": True}
    assert client.put(f"/tasks/{t['id']}", json={"title": " "}).status_code == 400


def test_delete_task(client):
    t = client.post("/tasks", json={"title": "tmp"}).get_json()
    assert client.delete(f"/tasks/{t['id']}").status_code == 204
    assert client.get(f"/tasks/{t['id']}").status_code == 404
    assert client.delete(f"/tasks/{t['id']}").status_code == 404


def test_missing_task_returns_404(client):
    assert client.get("/tasks/nope").status_code == 404
    assert client.put("/tasks/nope", json={"done": True}).status_code == 404


def test_metrics_exposed(client):
    client.post("/tasks", json={"title": "m"})
    body = client.get("/metrics").get_data(as_text=True)
    assert "taskflow_http_requests_total" in body
    assert "taskflow_tasks_total 1.0" in body
    assert "taskflow_build_info" in body
