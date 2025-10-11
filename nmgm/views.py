from os import name
from django.http import HttpResponse
from .models import User, Chatroom
from .logic import ChatroomProcessor
import pandas as pd


def home(request):
    return HttpResponse("Hello, NMGM!")


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

def generate_chatroom_report(request):
    pass


def generate_user_report(request):
    pass


def suggest_message_edit(request):
    pass
