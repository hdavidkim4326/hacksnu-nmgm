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
# views.py

@csrf_exempt
def import_data(request):
    if request.method != "POST" or not request.FILES.get("file"):
        return JsonResponse({"error": "Invalid request. A file must be POSTed."}, status=400)

    try:
        uploaded_file = request.FILES["file"]
        dataframe = pd.read_csv(uploaded_file)
        filepath = os.path.join("chats", uploaded_file.name)
        
        chatroom, is_new = Chatroom.objects.get_or_create(name=filepath)
        
        if is_new:
            chatroom.load(dataframe)
        
        # --- 여기가 핵심 수정 부분 ---
        # 파일 처리 후, 바로 리포트 에이전트를 호출하여 리포트를 생성합니다.
        report_agent = ChatroomReportAgent(
            chatroom=chatroom, api_key=os.getenv("GEMINI_KEY")
        )
        report_data = report_agent.generate_report()
        
        # 생성된 리포트 데이터를 JSON 형태로 프론트엔드에 반환합니다.
        return JsonResponse(report_data, status=200)

    except Exception as e:
        print(f"CRITICAL Error in import_data: {e}")
        return JsonResponse({"error": str(e)}, status=500)

# ... 나머지 함수들은 그대로 ...



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
