from django.shortcuts import render

def index(request):
    return render(request, 'nmgm/main.html')
def user_detail(request):
    return render(request, 'nmgm/user_detail.html')
def landing(request):
    return render(request, 'nmgm/landing.html')

def main_view(request):
    # 실제로는 DB에서 해당 유저의 데이터를 조회해야 합니다.
    context = {
        'user': {
            'name': '김하윤',
        },
        'habits_report': {
            'feedback': '이번주는 부드러운 한 주 였어요. 공손한 말투가 늘었고, 괜찮아요 표현의 사용이 잦았어요 🙂',
            'positive_score': 85,
        },
        'chat_rooms': [
            {
                'id': 1,
                'profile_image_url': 'https://example.com/profile1.png',
                'name': 'Ronald Richards',
                'last_message_time': '11:25',
                'last_message_preview': '다음에 가면 너무 좋겠...',
                'summary_text': '서로의 대화 템포가 잘 맞아요',
                'keywords': ['공감형', '활발한 대화', '감정 풍부'],
            },
            {
                'id': 2,
                'profile_image_url': 'https://example.com/profile2.png',
                'name': 'Esther Howard',
                'last_message_time': '10:58',
                'last_message_preview': '회의록 정리해서 보내드릴게요!',
                'summary_text': '주로 업무 관련 대화가 많아요',
                'keywords': ['업무 중심', '간결한 소통', '정보 공유'],
            },
        ]
    }
    return render(request, 'nmgm/main.html', context)