from os import name
from django.http import HttpResponse
<<<<<<< HEAD
from .models import User
=======
from .models import User, Chatroom
from .logic import ChatroomProcessor
import pandas as pd

>>>>>>> 8136b315 ([add thread cut])

def home(request):
    return HttpResponse("Hello, NMGM!")

<<<<<<< HEAD
def add_user(request):
    if request.method == "GET":
        name = request.GET.get("name")
        email = request.GET.get("email")
        user = User(name=name, email=email)
        user.save()
        return HttpResponse(f"User {name} added successfully.")

def add_message(request):
    pass
=======

def import_data(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    dataframe = pd.read_csv(filepath)
    chatroom, is_new = Chatroom.objects.get_or_create(name=filepath)
    if is_new:
        chatroom.load(dataframe)

    # FIXME : 나중에는 is_new 안으로 옮겨서 한꺼번에
    chatroom_processor = ChatroomProcessor(chatroom=chatroom, create_pipeline=True)
    chatroom_processor.pipeline()
    chatroom.save()
    return HttpResponse("Chatroom created")

def clear_threads(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    chatroom = Chatroom.objects.get(name=filepath)
    chatroom_processor = ChatroomProcessor(chatroom=chatroom)
    chatroom_processor.clear_threads()
    return HttpResponse("Threads cleared")
>>>>>>> 8136b315 ([add thread cut])

def generate_chatroom_report(request):
    pass

<<<<<<< HEAD
def generate_user_report(request):
    pass

def suggest_message_edit(request):
    pass
=======

def generate_user_report(request):
    pass


def suggest_message_edit(request):
    pass
>>>>>>> 8136b315 ([add thread cut])
