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
        filepath = uploaded_file.name
        
        chatroom, is_new = Chatroom.objects.get_or_create(name=filepath)
        
        if is_new:
            chatroom.load(dataframe)

        Loader(api_key=os.getenv("GEMINI_KEY"), chatroom=chatroom).load_chatroom()
        
        # --- 여기가 핵심 수정 부분 ---
        # 파일 처리 후, 바로 리포트 에이전트를 호출하여 리포트를 생성합니다.
        report_agent = ChatroomReportAgent(
            chatroom=chatroom, api_key=os.getenv("GEMINI_KEY")
        )
        report_data = report_agent.generate_report()
        # report_data = '{"chatsummary":{"summary":"김주형님과 김하윤님은 ERD Cloud 사용 문제 해결을 위해 DBML 스키마 공유, 미팅, 깃허브 레포지토리 설정 등 협업 과정에서 발생하는 기술 적인 어려움을 겪었습니다. 깃허브 권한 문제로 fork를 결정하고 Vercel 배포 가능성을 확인하며, 다음 날 코드 통합 및 테스트를 위해 학교에서 만나기로 약속했습니다.  이후 Notion 링크와 파이썬 패키지 정보를 공유하고, 만남 장소에 도착 시간 관련하여 서로 소통했습니다.","start_time":"2025-10-06T10:48:10Z","end_time":"2025-10-17T21:34:36Z","threads":[{"topic_summary":"김주형님이 김하윤님에게 ERD Cloud 사용 관련 어려움을 언급하며 DBML로 스키마를 짜서 공유하고, 오후 1시에 미팅 링크를 통해 만나자는 메시지를 보냈습니다. 김하윤님은 감사 인사를 전하며 미팅을 확인했습니다.","chat_type":"정보교환","num_messages":5,"avg_emotions":[{"emotion":"joy","score":0.44},{"emotion":"sadness","score":0.08},{"emotion":"anger","score":0.03},{"emotion":"fear","score":0.03},{"emotion":"surprise","score":0.26},{"emotion":"disgust","score":0.02}],"duration":4.65},{"topic_summary":"김하윤님이 저녁 전까지 깃허브에 필요한 내용을 준비하겠다고 전달하고, 김주형님이 이에 대해 감사 인사를  표했습니다. 이는 작업 진행 상황에 대한 정보 교환으로 보입니다.","chat_type":"정보교환","num_messages":2,"avg_emotions":[{"emotion":"joy","score":0.45},{"emotion":"sadness","score":0.1},{"emotion":"anger","score":0.05},{"emotion":"fear","score":0.05},{"emotion":"surprise","score":0.15},{"emotion":"disgust","score":0.05}],"duration":1.3},{"topic_summary":"김하윤님은 깃허브 레포지토리 설정 접근 권한 문제로 김주형님에게 admin 권한을 요청했고, 개인 계정에서는 admin 권한을 줄 수 없다는 것을 확인 후 fork를 통해 문제를 해결하기로 결정했습니다. Vercel 배포를 위해 레포지토리 설정을 변경하는 과정에서 권한 문제가 발생했으며, fork 후 배포 가능성을 확인해보기로 했습니다.","chat_type":"의사결정","num_messages":17,"avg_emotions":[{"emotion":"joy","score":0.17},{"emotion":"sadness","score":0.16},{"emotion":"anger","score":0.08},{"emotion":"fear","score":0.11},{"emotion":"surprise","score":0.25},{"emotion":"disgust","score":0.07}],"duration":35.5},{"topic_summary":"김주형님은 김하윤님에게 내일 코드를 합치고 테스트하기 위해 만날 수 있는지 물어봤고, 김하윤님은 시험이 끝난 후 학교에서 만나자는 답을 했습니다. 이후 두 사람은 만날 장소를 정하고, 김주형님이 44-1동 401-2호에 예약했다는 정보를 공유했습니다.","chat_type":"의사결정","num_messages":7,"avg_emotions":[{"emotion":"joy","score":0.59},{"emotion":"sadness","score":0.1},{"emotion":"anger","score":0.04},{"emotion":"fear","score":0.07},{"emotion":"surprise","score":0.33},{"emotion":"disgust","score":0.04}],"duration":192.78},{"topic_summary":"김주형님이 Notion 링크를 공유했으며, 그 후 여러 파이썬 패키지 목록과 버전을 공유했습니다.","chat_type":"정보교환","num_messages":2,"avg_emotions":[{"emotion":"joy","score":0.05},{"emotion":"sadness","score":0.05},{"emotion":"anger","score":0.05},{"emotion":"fear","score":0.05},{"emotion":"surprise","score":0.05},{"emotion":"disgust","score":0.05}],"duration":4.8},{"topic_summary":"김하윤님이 김주형님의 도착 여부를 묻고  김주형님은 곧 도착한다고 답한 후 도착했음을 알립니다. 김하윤님은 이제 출발해서 늦을 것 같다고 전달합니다.","chat_type":"정보교환","num_messages":4,"avg_emotions":[{"emotion":"joy","score":0.28},{"emotion":"sadness","score":0.1},{"emotion":"anger","score":0.05},{"emotion":"fear","score":0.05},{"emotion":"surprise","score":0.28},{"emotion":"disgust","score":0.05}],"duration":14.02}]},"user_analysis":[{"username":"해커톤 김하윤","personality":"표현형","description":"김하윤님은  비교적 부드럽고 친근한 어조로 대화하며, 평균 응답 시간이 짧고 먼저 연락하는 비율이 높아 적극적인 소통을 선호하는 것으로 보입니다. 감정적인 표현은 다소 절제되어 있지만, 즐거움을 표현하는 빈도가 다른 부정적인 감정보다 높습니다.","avg_indices":[{"index":"directness","score":0.49},{"index":"softness","score":0.61},{"index":"emotionality","score":0.37},{"index":"logicality","score":0.34},{"index":"dominance","score":0.29},{"index":"friendliness","score":0.65}],"avg_emotions":[{"emotion":"joy","score":0.21},{"emotion":"sadness","score":0.16},{"emotion":"anger","score":0.06},{"emotion":"fear","score":0.09},{"emotion":"surprise","score":0.16},{"emotion":"disgust","score":0.05}],"median_response_time":2.38,"initiative_rate":0.6,"messages":[{"sent_time":"2025-10-06T10:52:49Z","sentiment":0.8},{"sent_time":"2025-10-06T13:23:52Z","sentiment":-0.1},{"sent_time":"2025-10-13T15:07:55Z","sentiment":-0.3},{"sent_time":"2025-10-13T15:39:31Z","sentiment":0.0},{"sent_time":"2025-10-13T15:39:58Z","sentiment":-0.3},{"sent_time":"2025-10-13T15:40:24Z","sentiment":-0.4},{"sent_time":"2025-10-13T15:40:48Z","sentiment":-0.0},{"sent_time":"2025-10-13T15:40:55Z","sentiment":-1.1},{"sent_time":"2025-10-13T15:41:25Z","sentiment":-0.4},{"sent_time":"2025-10-13T15:43:01Z","sentiment":0.2},{"sent_time":"2025-10-16T13:20:47Z","sentiment":0.6},{"sent_time":"2025-10-16T14:03:30Z","sentiment":0.8},{"sent_time":"2025-10-17T20:44:19Z","sentiment":0.2},{"sent_time":"2025-10-17T20:58:20Z","sentiment":0.1}]},{"username":"김주형","personality":"표현형","description":"김주형님은 비교적 직접적이고 감정적인 표현을 사용하며, 즐거움과 놀라움을 나타내는 텍스트를 보낼 가능성이 높습니다. 또한, 평균 응답 시간이 9.43초로 비교적 빠른 편이며, 먼저 연락을 시도하는 비율도 중간 정도입니 다.","avg_indices":[{"index":"directness","score":0.46},{"index":"softness","score":0.42},{"index":"emotionality","score":0.41},{"index":"logicality","score":0.19},{"index":"dominance","score":0.28},{"index":"friendliness","score":0.53}],"avg_emotions":[{"emotion":"joy","score":0.36},{"emotion":"sadness","score":0.1},{"emotion":"anger","score":0.06},{"emotion":"fear","score":0.07},{"emotion":"surprise","score":0.3},{"emotion":"disgust","score":0.06}],"median_response_time":9.43,"initiative_rate":0.5,"messages":[{"sent_time":"2025-10-06T10:48:10Z","sentiment":0.3},{"sent_time":"2025-10-06T10:49:28Z","sentiment":0.8},{"sent_time":"2025-10-06T10:49:29Z","sentiment":0.0},{"sent_time":"2025-10-06T10:50:26Z","sentiment":0.8},{"sent_time":"2025-10-06T13:25:10Z","sentiment":0.8},{"sent_time":"2025-10-13T15:25:36Z","sentiment":0.5},{"sent_time":"2025-10-13T15:27:04Z","sentiment":0.0},{"sent_time":"2025-10-13T15:27:11Z","sentiment":0.9},{"sent_time":"2025-10-13T15:40:26Z","sentiment":-0.1},{"sent_time":"2025-10-13T15:40:30Z","sentiment":-0.0},{"sent_time":"2025-10-13T15:41:55Z","sentiment":0.6},{"sent_time":"2025-10-13T15:41:55Z","sentiment":-0.2},{"sent_time":"2025-10-13T15:42:13Z","sentiment":-0.3},{"sent_time":"2025-10-13T15:43:25Z","sentiment":0.8},{"sent_time":"2025-10-16T12:57:06Z","sentiment":0.6},{"sent_time":"2025-10-16T12:57:35Z","sentiment":0.7},{"sent_time":"2025-10-16T13:35:07Z","sentiment":0.9},{"sent_time":"2025-10-16T13:35:17Z","sentiment":-0.0},{"sent_time":"2025-10-16T16:09:53Z","sentiment":1.0},{"sent_time":"2025-10-17T20:53:45Z","sentiment":0.6},{"sent_time":"2025-10-17T20:57:53Z","sentiment":0.3},{"sent_time":"2025-10-17T21:29:48Z","sentiment":-0.2},{"sent_time":"2025-10-17T21:34:36Z","sentiment":0.0}]}],"warnings":[{"message":"아 진짜 답답하네 왜 안되지 (추정)","sent_by":"해커톤 김하윤","key_emotion":"anger","warning_type":"감정해석차이","detail":"깃허브 권한 문제 해결 과정에서 김하윤님의 감정이 급격히 부정적(-1.1)으로 표현되었습니다. 이는 문제 상황에 대한 답답함에서 비롯된 것이지만, 상대방은 자신에 대한 분노나 비난으로 오해할 수 있어 감정 해석의 차이를 유발하고 갈등으로 이어질 수 있습니다. 평소 친근한 소통 스타일과 대비되는 강한 부정적 표현은 상대방에게 더 큰 혼란을 줄 수 있습니다.","action_plan":"김하윤님은 \'표현형\' 성향으로 감정 표현이 중요하지만, 부정적 감정은 오해를 살 수 있습니다. 문제 상황으로 인한 답답함이 생길 때, 감정을 표출하기보다 \'이 문제가 잘 안 풀려서 답답하네요\'와 같이 감정의 원인을 명확히 설명하는 \'I-message\' 화법을 사용하는 것이 좋습니다. 또한, \'혹시 다른 방법이 있을까요?\'처럼 해결 중심의 질문을 덧붙이면, 개인적인 공격이 아닌 문제 해결에 집중하고 있다는 긍정적인 신호를 주어 원활한 협업을 이어갈 수 있습니다."}]}'
        
        # 생성된 리포트 데이터를 JSON 형태로 프론트엔드에 반환합니다.
        return JsonResponse(report_data, status=200, safe=False)

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
    filepath = request.GET.get("filepath")  # ex. chat_01.csv
    chatroom = Chatroom.objects.get(name=filepath)
    report = ChatroomReportAgent(
        chatroom=chatroom, api_key=os.getenv("GEMINI_KEY")
    ).generate_report()
    #breakpoint()
    return JsonResponse(report, safe=False)


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