import pytest

from commands.models import Command

pytestmark = pytest.mark.regression

def test_str_returns_name():
    assert str(Command(name="move")) == "move"

@pytest.mark.django_db
def test_defaults():
    c = Command.objects.create(name="move")
    assert c.status == "pending"
    assert c.priority == 0


@pytest.mark.django_db
def test_newest_first_ordering():
    first = Command.objects.create(name="first")
    second = Command.objects.create(name="second")
    assert list(Command.objects.all()) == [second, first]