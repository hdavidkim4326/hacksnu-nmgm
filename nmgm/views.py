from django.http import HttpResponse
from django.shortcuts import render
from .models import Chatroom, User
from .logic import ChatroomProcessor
from .agents import ChatroomReportAgent, UserReportAgent, NextMessageEditAgent
import pandas as pd

def landing_view(request):
    return render(request, 'nmgm/landing.html')

def prototype_view(request):
    return render(request, 'nmgm/prototype.html')
def report_view(request):
    return render(request, 'nmgm/report.html')


def import_data(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    dataframe = pd.read_csv(filepath)
    chatroom, is_new = Chatroom.objects.get_or_create(name=filepath)
    if is_new:
        chatroom.load(dataframe)

    chatroom_processor = ChatroomProcessor(chatroom=chatroom)
    chatroom_processor.pipeline()
    chatroom.save()
    return HttpResponse("Chatroom created")


def clear_threads(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    chatroom = Chatroom.objects.get(name=filepath)
    chatroom_processor = ChatroomProcessor(chatroom=chatroom)
    chatroom_processor.clear_threads()
    return HttpResponse("Threads cleared")


def clear_emotions(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    chatroom = Chatroom.objects.get(name=filepath)
    chatroom_processor = ChatroomProcessor(chatroom=chatroom)
    chatroom_processor.clear_emotions()
    return HttpResponse("Emotions cleared")


def generate_chatroom_report(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    chatroom = Chatroom.objects.get(name=filepath)
    report = ChatroomReportAgent(
        chatroom=chatroom, api_key=os.getenv("GEMINI_KEY")
    ).generate_chatroom_report()
    return HttpResponse("Chatroom report generated")


def generate_user_report(request):
    user_id = request.GET.get("user")  # ex. 1
    user = User.objects.get(id=user_id)
    report = UserReportAgent(
        user=user, api_key=os.getenv("GEMINI_KEY")
    ).generate_user_report()
    return HttpResponse("User report generated")


def suggest_message_edit(request):
    user_id = 3
    chatroom = Chatroom.objects.get(name="chats/chat_01.csv")
    user = User.objects.get(id=user_id)

    next_message = NextMessageEditAgent(
        api_key=os.getenv("GEMINI_KEY")
    ).suggest_message(
        user=user, chatroom=chatroom, message = "너 나 사랑하는 거 맞아?"
    )
