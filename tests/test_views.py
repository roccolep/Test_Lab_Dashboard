import pytest

from commands.models import Command

pytestmark = pytest.mark.regression

@pytest.mark.smoke
@pytest.mark.django_db
def test_index_view(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Test Lab Dashboard" in response.content

@pytest.mark.smoke
@pytest.mark.django_db
def test_form_submit_saves_command(client):
    client.post("/", {"name": "move", "payload": '{"unit": "A1"}', "priority": 1})
    assert Command.objects.count() == 1

@pytest.mark.django_db
def test_submit_runs_mock_target(client):
    client.post("/", {"name": "move", "payload": '{"unit": "A1"}', "priority": 1})
    cmd = Command.objects.get()
    assert cmd.status == "completed"
    assert "ACK" in cmd.reply


@pytest.mark.django_db
def test_failed_command_is_marked_failed(client):
    client.post("/", {"name": "move", "payload": "{}", "priority": 1})
    assert Command.objects.get().status == "failed"


@pytest.mark.django_db
@pytest.mark.parametrize("data", [
    {"name": "", "payload": '{"unit": "A1"}', "priority": 1},
    {"name": "move", "payload": "[1, 2]", "priority": 1},
    {"name": "move", "payload": "hello", "priority": 1},
])
def test_invalid_submit_saves_nothing(client, data):
    client.post("/", data)
    assert Command.objects.count() == 0


@pytest.mark.django_db
def test_valid_submit_redirects(client):
    response = client.post("/", {"name": "move", "payload": '{"unit": "A1"}', "priority": 1})
    assert response.status_code == 302