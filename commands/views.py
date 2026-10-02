from django.shortcuts import render
from .models import Command

# Create your views here.
def index(request):
    commands = Command.objects.all()
    return render(request, "commands/index.html", {"commands": commands})