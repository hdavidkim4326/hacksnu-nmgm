from os import name
from django.http import HttpResponse
from .models import User

def home(request):
    return HttpResponse("Hello, NMGM!")

def add_user(request):
    if request.method == "GET":
        name = request.GET.get("name")
        email = request.GET.get("email")
        user = User(name=name, email=email)
        user.save()
        return HttpResponse(f"User {name} added successfully.")
