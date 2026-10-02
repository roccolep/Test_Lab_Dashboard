import re

from .models import Command

all_commands = ["move", "stop", "load"]

def mock_target(command: Command):
    payload = command.payload or []
    if "unit" not in payload:
        return "failed", "ERROR: missing 'unit'"
    if command.name not in all_commands:
        return "failed", f"ERROR: unknown command '{command.name}'"
    unit = payload['unit']
    if not isinstance(unit, str) or not re.fullmatch(r"[A-Z][0-9]+", unit):
        return "failed", f"ERROR: invalid unit '{unit}' (expected like A1)"
    return "completed", f"ACK: {command.name} -> unit {payload['unit']}"

def submit(command: Command):
    command.save()
    status, reply = mock_target(command)
    command.status = status
    command.reply = reply
    command.save()
    return command