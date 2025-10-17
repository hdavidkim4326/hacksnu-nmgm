from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Chatroom, User
from .agents.agents import Loader, ChatroomReportAgent, UserReportAgent, MessageEditor
import pandas as pd
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
load_dotenv()

def landing_view(request):
    return render(request, 'nmgm/landing.html')

def prototype_view(request):
    return render(request, 'nmgm/prototype.html')
    
def report_view(request):
    return render(request, 'nmgm/report.html')


@csrf_exempt
def import_data(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        filepath = os.path.join("chats", uploaded_file.name)
        with open(filepath, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
    else:
        filepath = "chats/" + request.GET.get("filepath")
    breakpoint()
    dataframe = pd.read_csv(filepath)
    chatroom, is_new = Chatroom.objects.get_or_create(name=filepath)
    if is_new:
        chatroom.load(dataframe)
    chatroom_processor = Loader(api_key=os.getenv("GEMINI_KEY"), chatroom=chatroom)
    chatroom_processor.load_chatroom()
    chatroom.save()
    return HttpResponse("Chatroom created")


def clear_threads(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    chatroom = Chatroom.objects.get(name=filepath)
    chatroom_processor = Loader(api_key = os.getenv("GEMINI_KEY"), chatroom=chatroom)
    chatroom_processor.clear_threads()
    return HttpResponse("Threads cleared")


def clear_emotions(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    chatroom = Chatroom.objects.get(name=filepath)
    chatroom_processor = Loader(api_key = os.getenv("GEMINI_KEY"), chatroom=chatroom)
    chatroom_processor.clear_msg_metadata()
    return HttpResponse("Emotions cleared")


def generate_chatroom_report(request):
    filepath = "chats/" + request.GET.get("filepath")  # ex. chat_01.csv
    chatroom = Chatroom.objects.get(name=filepath)
    report = ChatroomReportAgent(
        chatroom=chatroom, api_key=os.getenv("GEMINI_KEY")
    ).generate_report()
    breakpoint()
    return JsonResponse(report)


def generate_user_report(request):
    user_id = request.GET.get("user")  # ex. 1
    user = User.objects.get(id=user_id)
    report = UserReportAgent(
        user=user, api_key=os.getenv("GEMINI_KEY")
    ).generate_report()
    return JsonResponse(report)


def suggest_message_edit(request):
    user_id = 3
    chatroom = Chatroom.objects.get(name="chats/chat_01.csv")
    user = User.objects.get(id=user_id)
    next_message = MessageEditor(
        api_key=os.getenv("GEMINI_KEY")
    ).suggest_message(
        user=user, chatroom=chatroom, message = "너 나 사랑하는 거 맞아?"
    )
    return JsonResponse(next_message)


def generate_chatroom_report(request):

    filepath = "chats/" + request.GET.get("filepath", "chat_01.csv")
    chatroom = Chatroom.objects.get(name=filepath)
    report = ChatroomReportAgent(
        chatroom=chatroom, api_key=os.getenv("GEMINI_KEY")
    ).generate_report()
    return JsonResponse(report)
