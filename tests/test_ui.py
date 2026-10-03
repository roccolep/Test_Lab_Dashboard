import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import pytest
from playwright.sync_api import expect

from commands.models import Command

pytestmark = [pytest.mark.ui, pytest.mark.django_db(transaction=True)]


def send_command(page, name, payload, priority="1"):
    """Fill in the form on the page and click Send."""
    page.fill("#id_name", name)
    page.fill("#id_payload", payload)
    page.select_option("#id_priority", priority)
    page.click("button[type=submit]")


def test_empty_state_message(live_server, page):
    page.goto(live_server.url)
    expect(page.locator("#history")).to_contain_text("No commands yet")


def test_valid_command_shows_completed(live_server, page):
    page.goto(live_server.url)
    send_command(page, "move", '{"unit": "A1"}')

    history = page.locator("#history")
    expect(history).to_contain_text("move")
    expect(history).to_contain_text("Completed")
    expect(history).to_contain_text("ACK: move -> unit A1")
    assert Command.objects.count() == 1


def test_missing_unit_shows_failed(live_server, page):
    page.goto(live_server.url)
    send_command(page, "move", '{"target": "A1"}')

    history = page.locator("#history")
    expect(history).to_contain_text("Failed")
    expect(history).to_contain_text("ERROR: missing 'unit'")


def test_unknown_command_shows_failed(live_server, page):
    page.goto(live_server.url)
    send_command(page, "dance", '{"unit": "A1"}')

    history = page.locator("#history")
    expect(history).to_contain_text("Failed")
    expect(history).to_contain_text("unknown command")


def test_invalid_json_shows_error_and_saves_nothing(live_server, page):
    page.goto(live_server.url)
    send_command(page, "move", "hello")

    expect(page.locator(".errorlist")).to_be_visible()
    expect(page.locator(".errorlist")).to_contain_text("valid JSON")
    expect(page.locator("#history")).to_contain_text("No commands yet")
    assert Command.objects.count() == 0


def test_payload_must_be_an_object(live_server, page):
    page.goto(live_server.url)
    send_command(page, "move", "[1, 2]")

    expect(page.locator(".errorlist")).to_be_visible()
    assert Command.objects.count() == 0


def test_blank_name_shows_required_error(live_server, page):
    page.goto(live_server.url)
    send_command(page, "   ", '{"unit": "A1"}')

    expect(page.locator(".errorlist")).to_contain_text("required")
    assert Command.objects.count() == 0


def test_newest_command_is_listed_first(live_server, page):
    page.goto(live_server.url)
    send_command(page, "move", '{"unit": "A1"}')
    expect(page.locator("#history")).to_contain_text("ACK: move")
    send_command(page, "stop", '{"unit": "B2"}')
    expect(page.locator("#history")).to_contain_text("ACK: stop")

    first_row = page.locator("#history tbody tr").first
    expect(first_row).to_contain_text("stop")


def test_form_resets_after_successful_submit(live_server, page):
    page.goto(live_server.url)
    send_command(page, "move", '{"unit": "A1"}')
    expect(page.locator("#history")).to_contain_text("ACK: move")
    expect(page.locator("#id_name")).to_have_value("")

    page.reload()
    assert Command.objects.count() == 1