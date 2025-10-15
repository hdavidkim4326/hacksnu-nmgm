from audioop import avg
import datetime
from mimetypes import init
from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum

# ========= ENUMERATIONS ===========

class Emotion(str, Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"

class ConversationIndex(str, Enum):
    DIRECTNESS = "directness"
    SOFTNESS = "softness"
    EMOTIONALITY = "emotionality"
    LOGICALITY = "logicality"
    DOMINANCE = "dominance"
    FRIENDLINESS = "friendliness"

class UserType(str, Enum):
    EXPRESSIVE = "표현형"
    INSTINCTIVE = "본능형"
    COMMANDER = "지시형"
    PRECISOR = "정밀형"
    HARMONIZER = "조화형"
    EMPATHIZER = "공감형"
    ANALYST = "분석형"
    MEDIATOR = "중재형"

class SentenceClarity(str, Enum):
    VERY_CLEAR = "매우 명확함"
    CLEAR = "명확함"
    AVERAGE = "보통"
    UNCLEAR = "명확하지 않음"
    VERY_UNCLEAR = "매우 명확하지 않음"

class ChatType(str, Enum):
    DECISION_MAKING = "의사결정"
    SHARING_EMOTIONS = "감정공유"
    CONFLICT_MANAGEMENT = "갈등관리"
    INFORMATION_EXCHANGE = "정보교환"
    JOKES_AND_CHITCHAT = "농담및잡담"

class WarningType(str, Enum):
    EMOTION_DISCREPANCY = "감정해석차이"
    SEMANTIC_DISCREPANCY = "의미불일치"

# ======== USER REPORT ===========

class PosTag(BaseModel):
    tag: str
    rate: float

class WordCount(BaseModel):
    word: str
    count: int

class EmotionOutput(BaseModel):
    emotion: Emotion
    score: float = Field(..., ge=0.0, le=1.0)

class ConversationIndexOutput(BaseModel):
    index: ConversationIndex
    score: float = Field(..., ge=-1.0, le=1.0)

class Strength(BaseModel):
    strength: str

class Weakness(BaseModel):
    weakness: str

class ActionPlan(BaseModel):
    action_plan: str

# ======== CHATROOM REPORT ===========

class ThreadInfo(BaseModel):
    topic_summary: str
    chat_type: ChatType
    num_messages: int
    avg_emotions: list[EmotionOutput]
    duration: float

class ChatSummary(BaseModel):
    summary: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    threads: list[ThreadInfo]

class BriefMessageInfo(BaseModel):
    sent_time: datetime.datetime
    sentiment: float

class UserAnalysis(BaseModel):
    username: str
    personality: UserType
    description: str
    avg_indices: list[ConversationIndexOutput]
    avg_emotions: list[EmotionOutput]
    median_response_time: float
    initiative_rate: float
    messages: list[BriefMessageInfo]

class ChatWarningCandidate(BaseModel):
    message: str
    username: str
    sent_time: datetime.datetime
    response_delay: float
    emotion_vector: list[EmotionOutput]
    response_emotion_vector: list[EmotionOutput]

class ChatWarning(BaseModel):
    message: str
    sent_by: str
    key_emotion: str
    warning_type: WarningType
    detail: str
    action_plan: str

# ========= FINAL REPORT TYPES ===========

class UserReport(BaseModel):
    username: str
    median_response_time: float
    avg_msg_length: float
    initiative_rate: float
    message_count: int
    chatroom_count: int
    thread_count: int
    emoji_avg: float
    pos_tags: list[PosTag]
    word_counts: list[WordCount]
    avg_emotions: list[EmotionOutput]
    avg_indices: list[ConversationIndexOutput]
    user_type: UserType
    summary: str
    strengths: list[Strength]
    weaknesses: list[Weakness]
    sentence_clarity: SentenceClarity
    action_plans: list[ActionPlan]

class ChatroomReport(BaseModel):
    chatsummary: ChatSummary
    user_analysis: list[UserAnalysis]
    warnings: list[ChatWarning]

# ========= NEXT MESSAGE EDIT ===========

class EditSuggestion(BaseModel):
    suggested_message: str
    reason: str

class NextMessageEdit(BaseModel):
    original_message: str
    suggestions: list[EditSuggestion]

# =========== TOOLS ===========
class IsRelated(BaseModel):
    related: bool

# =========== DB SCHEMA ==========
class MsgMetadata(BaseModel):
    emotions : list[EmotionOutput]
    indices : list[ConversationIndexOutput]
    num_sentences: int

class ThreadMetadata(BaseModel):
    topic_summary: str
    chat_type: ChatType