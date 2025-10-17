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


# ... 기존 코드 ...
@csrf_exempt
def import_data(request):
    # 파일 업로드 요청은 반드시 POST 방식이어야 합니다.
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        
        # [핵심 수정 1] 파일을 디스크에 저장하지 않고, 메모리에서 직접 pandas로 읽습니다.
        # Django의 UploadedFile 객체는 파일처럼 동작하여 바로 전달할 수 있습니다.
        dataframe = pd.read_csv(uploaded_file)
        
        # [핵심 수정 2] 파일 '이름'을 DB의 고유 식별자로 사용하기 위해 가상의 경로를 만듭니다.
        # 실제 서버 파일 시스템에 'chats' 폴더를 만들거나 파일을 저장하지 않습니다.
        filepath = os.path.join("chats", uploaded_file.name)
        with open(filepath, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
    else:
        filepath = "chats/" + request.GET.get("filepath")
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
    #breakpoint()
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
