# nmgm/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Keyword(models.Model):
    """
    #공감형, #활발한 대화 등 채팅방의 관계 키워드를 저장하는 모델
    """
    name = models.CharField(max_length=50, unique=True, help_text="관계 키워드 이름")

    def __str__(self):
        return self.name

class ChatRoom(models.Model):
    """
    메인 대시보드에 표시될 각 채팅방의 정보를 담는 모델
    """
    class PlatformChoices(models.TextChoices):
        KAKAO = 'KAKAO', '카카오톡'
        INSTAGRAM = 'INSTA', '인스타그램'
        SLACK = 'SLACK', '슬랙'

    # 이 채팅방을 분석한 유저 (User 모델과 다대일 관계)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')

    # 채팅방 기본 정보
    title = models.CharField(max_length=200, help_text="채팅방 이름 또는 상대방 이름")
    platform = models.CharField(max_length=10, choices=PlatformChoices.choices, default=PlatformChoices.KAKAO, help_text="채팅 플랫폼 종류")
    profile_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True, help_text="채팅방 대표 프로필 이미지")

    # 대시보드 표시에 필요한 요약 정보
    last_message_preview = models.CharField(max_length=255, blank=True, help_text="마지막 대화 미리보기")
    last_message_time = models.DateTimeField(null=True, blank=True, help_text="마지막 대화 시간")
    summary_text = models.TextField(blank=True, help_text="AI가 요약한 대화 문장")

    # 키워드 (Keyword 모델과 다대다 관계)
    keywords = models.ManyToManyField(Keyword, related_name='chat_rooms', blank=True)

    # 데이터 동기화 시간 추적
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at'] # 최근 업데이트된 순으로 정렬

    def __str__(self):
        return f"{self.user.username}의 {self.title} 채팅방"


class UserHabitReport(models.Model):
    """
    유저 한 명의 전체적인 대화 습관 리포트 정보를 저장하는 모델
    """
    # Django 기본 User 모델과 일대일 관계
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='habit_report')

    # 보라색 카드에 표시될 AI 피드백 및 감정 점수
    feedback_text = models.TextField(blank=True, help_text="AI의 주간 종합 피드백")
    positive_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="긍정 감정 점수 (0-100)"
    )

    # 리포트 갱신 시간
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}의 대화 습관 리포트"