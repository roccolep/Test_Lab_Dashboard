import json
import pytest
from commands.models import Command

pytestmark = [pytest.mark.regression, pytest.mark.api, pytest.mark.django_db]

MOCK_COMMAND = {
    "name": "move",
    "payload": {"unit": "A1"},
    "priority": 1,
}

def post_json(client, body):
    return client.post(
        "/api/commands/",
        data=json.dumps(body),
        content_type="application/json",
    )

@pytest.mark.smoke
def test_create_returns_201_and_completed(client):
    response = post_json(client, MOCK_COMMAND)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"
    assert data["name"] == "move"
    assert data["payload"] == {"unit": "A1"}
    assert "ACK" in data["reply"]
 
 
def test_create_saves_one_row(client):
    post_json(client, MOCK_COMMAND)
    assert Command.objects.count() == 1
 
 
def test_create_missing_unit_is_saved_as_failed(client):
    response = post_json(client, {"name": "move", "payload": {"target": "A1"}, "priority": 1})
    assert response.status_code == 201
    assert response.json()["status"] == "failed"
    assert "missing 'unit'" in response.json()["reply"]
 
 
def test_create_unknown_command_is_saved_as_failed(client):
    response = post_json(client, {"name": "dance", "payload": {"unit": "A1"}, "priority": 1})
    assert response.status_code == 201
    assert response.json()["status"] == "failed"
    assert "unknown command" in response.json()["reply"]
 
 
def test_create_invalid_unit_is_saved_as_failed(client):
    response = post_json(client, {"name": "move", "payload": {"unit": "a1"}, "priority": 1})
    assert response.status_code == 201
    assert response.json()["status"] == "failed"
 
def test_list_empty(client):
    response = client.get("/api/commands/")
    assert response.status_code == 200
    assert response.json() == {"results": []}
 
 
def test_list_returns_created_commands_newest_first(client):
    post_json(client, {**MOCK_COMMAND, "name": "move"})
    post_json(client, {**MOCK_COMMAND, "name": "stop"})
    response = client.get("/api/commands/")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()["results"]]
    assert names == ["stop", "move"]
 
def test_detail_returns_command(client):
    created = post_json(client, MOCK_COMMAND).json()
    response = client.get(f"/api/commands/{created['id']}/")
    assert response.status_code == 200
    assert response.json()["name"] == "move"
    assert response.json()["id"] == created["id"]
 
 
def test_detail_missing_returns_404(client):
    response = client.get("/api/commands/9999/")
    assert response.status_code == 404
    assert "error" in response.json()

def test_body_that_is_not_json_returns_400(client):
    response = client.post(
        "/api/commands/", data="hello", content_type="application/json"
    )
    assert response.status_code == 400
    assert Command.objects.count() == 0

def test_body_is_json(client):
    response = client.post(
        "/api/commands/", data=json.dumps(["not", "an", "object"]), content_type="application/json"
    )
    assert response.status_code == 400
    assert Command.objects.count() == 0

def test_body_is_missing_required_fields(client):
    response = client.post(
        "/api/commands/", data=json.dumps({"name": "move"}), content_type="application/json"
    )
    assert response.status_code == 400
    assert Command.objects.count() == 0

def test_method_not_allowed(client):
    response = client.put("/api/commands/")
    assert response.status_code == 405
    response = client.delete("/api/commands/")
    assert response.status_code == 405