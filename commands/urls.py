from django.urls import path
from .views import index
from commands import views

urlpatterns = [
    path('', index, name='index'),
   path("api/commands/", views.api_commands, name="api_commands"),
   path("api/commands/<int:pk>/", views.api_command_detail, name="api_command_detail"),
   ]