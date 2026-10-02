from django.shortcuts import render, redirect

from commands.services import submit
from .models import Command
from .forms import CommandForm

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
