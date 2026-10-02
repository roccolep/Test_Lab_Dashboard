import pytest

from commands.forms import CommandForm
from commands.models import Command

pytestmark = pytest.mark.regression

@pytest.mark.django_db
def test_command_form_valid_data():
    form_data = {
        'name': 'move',
        'payload': {'unit': 'A1'},
        'priority': 1
    }
    form = CommandForm(data=form_data)
    assert form.is_valid()
    command = form.save(commit=False)
    assert command.name == 'move'
    assert command.payload == {'unit': 'A1'}
    assert command.priority == 1


@pytest.mark.parametrize("data", [
    {"name": "", "payload": {"unit": "A1"}, "priority": 1},
    {"name": "move", "payload": [1, 2], "priority": 1},
    {"name": "move", "payload": 42, "priority": 1},
    {"name": "move", "payload": "hello", "priority": 1},
    {"name": "move", "payload": {"unit": "A1"}, "priority": 9},
])
def test_command_form_invalid_data(data):
    form = CommandForm(data=data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_command_form_saves_to_db():
    form = CommandForm(data={"name": "move", "payload": '{"unit": "A1"}', "priority": 1})
    assert form.is_valid()
    form.save()
    assert Command.objects.count() == 1

def test_command_form_empty_payload_is_invalid():
    form = CommandForm(data={"name": "move", "payload": "", "priority": 1})
    assert not form.is_valid()
    assert "payload" in form.errors