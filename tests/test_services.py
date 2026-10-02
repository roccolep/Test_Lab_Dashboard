import pytest

from commands.models import Command
from commands.services import mock_target

pytestmark = pytest.mark.regression

def test_mock_target():
    result = mock_target(Command(name="move", payload={"unit": "D4"}))
    assert result == ("completed", "ACK: move -> unit D4")

@pytest.mark.smoke
def test_completed_with_valid_unit():
    result = mock_target(Command(name="move", payload={"unit": "A5"}))
    assert result == ("completed", "ACK: move -> unit A5")


@pytest.mark.parametrize("payload", [{}, None, {"target": "A1"}])
def test_missing_unit_fails(payload):
    status, reply = mock_target(Command(name="move", payload=payload))
    assert status == "failed"
    assert reply == "ERROR: missing 'unit'"


@pytest.mark.parametrize("unit", ["a1", "A", "1A", "A1x", "", 123])
def test_invalid_unit_fails(unit):
    status, reply = mock_target(Command(name="move", payload={"unit": unit}))
    assert status == "failed"
    assert reply.startswith("ERROR: invalid unit")


def test_unknown_command_fails():
    status, reply = mock_target(Command(name="dance", payload={"unit": "A1"}))
    assert status == "failed"
    assert reply == "ERROR: unknown command 'dance'"