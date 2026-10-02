import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from commands.services import submit

from .forms import CommandForm
from .models import Command


# Create your views here.
def index(request):
    if request.method == "POST":
        form = CommandForm(request.POST)
        if form.is_valid():
            command = form.save(commit=False)
            submit(command)
            return redirect('index')
    else:
        form = CommandForm()
    return render(request, "commands/index.html", {"form": form, "commands": Command.objects.all()})

def command_to_dict(command: Command):
    return {
        "id": command.id,
        "name": command.name,
        "payload": command.payload,
        "priority": command.priority,
        "status": command.status,
        "reply": command.reply,
        "created_at": command.created_at.isoformat(),
    }

@csrf_exempt
def api_commands(request):
    if request.method == "GET":
        commands = Command.objects.all()
        return JsonResponse({"results": [command_to_dict(c) for c in commands]})
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except ValueError:
            return JsonResponse({"error": "Body must be valid JSON."}, status=400)
        if not isinstance(body, dict):
            return JsonResponse({"error": "Body must be a JSON object."}, status=400)

        form = CommandForm(body)
        if not form.is_valid():
            return JsonResponse({"error": form.errors.get_json_data()}, status=400)

        command = form.save(commit=False)
        submit(command)
        return JsonResponse(command_to_dict(command), status=201)
    return JsonResponse({"error": "Method not allowed."}, status=405)

def api_command_detail(request, pk):
    try:
        command = Command.objects.get(pk=pk)
    except Command.DoesNotExist:
        return JsonResponse({"error": "Not found."}, status=404)
    return JsonResponse(command_to_dict(command))