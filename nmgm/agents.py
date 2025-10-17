import datetime
from django.db.models import QuerySet
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal
from nmgm.models import Chatroom, ChatroomUser, Thread, Message, User
from dotenv import load_dotenv
import os
from textwrap import dedent
from konlpy.tag import Kkma, Okt
from collections import Counter
from sentence_transformers import SentenceTransformer
from django.db.models import F
from pgvector.django import CosineDistance

load_dotenv()

kkma = Kkma()
tagset = kkma.tagset


class Relatedness(BaseModel):
    related: bool


class Emotion(BaseModel):
    emotion: Literal["joy", "sadness", "anger", "fear", "surprise", "disgust"]
    score: float = Field(..., ge=0.0, le=1.0)


class Index(BaseModel):
    index: Literal[
        "directness",
        "softness",
        "emotionality",
        "logicality",
        "dominance",
        "friendliness",
    ]
    score: float = Field(..., ge=-1.0, le=1.0)


class MsgMetadata(BaseModel):
    emotions: list[Emotion]
    indices: list[Index]
    num_sentences: int


class ThreadMetadata(BaseModel):
    topic_summary: str
    chat_type: Literal[
        "Decision Making",
        "Sharing Emotions",
        "Conflict Management",
        "Information Exchange",
        "Jokes and Chit-chat",
    ]


class UserMetadata(BaseModel):
    median_response_time: float | None
    avg_msg_length: float | None
    initiative_rate: float | None
    avg_indices: dict[str, float]
    avg_emotions: dict[str, float]
    pos_tags: dict[str, float]
    frequently_used_words: dict[str, int]
    message_count: int
    chatroom_count: int
    thread_count: int
    emoji_avg: float


class UserReport(BaseModel):
    user_type: Literal[
        "표현형", "본능형", "지시형", "정밀형", "조화형", "공감형", "분석형", "중재형"
    ]
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    sentence_clarity: Literal["높음", "보통", "낮음"]
    action_plan: list[str]


class ThreadUserData(BaseModel):
    thread_id: int
    user_id: int
    num_messages: int
    avg_emotions: dict[str, float]
    avg_indices: dict[str, float]
    start_time: datetime.datetime


class SingleUserData(BaseModel):
    user_id: int
    username: str
    num_messages: int
    personality: (
        Literal[
            "표현형",
            "본능형",
            "지시형",
            "정밀형",
            "조화형",
            "공감형",
            "분석형",
            "중재형",
        ]
        | None
    )
    initiative_rate: float
    avg_msg_length: float
    median_response_time: float | None
    avg_indices: dict[str, float]
    avg_emotions: dict[str, float]
    thread_data: list[ThreadUserData]


class SingleThreadData(BaseModel):
    thread_id: int
    topic_summary: str
    chat_type: Literal[
        "Decision Making",
        "Sharing Emotions",
        "Conflict Management",
        "Information Exchange",
        "Jokes and Chit-chat",
    ]
    num_messages: int
    avg_emotions: dict[str, float]
    key_messages: list[int]
    duration_minutes: float
    start_time: datetime.datetime
    end_time: datetime.datetime


class ChatWarning(BaseModel):
    message: str
    user_id: int
    key_emotion: str
    warning_type: Literal["감정해석차이", "의미불일치"]
    signs: str
    detail_and_remedy: str


class ChatWarningCandidate(BaseModel):
    message: str
    user_id: int
    sent_time: datetime.datetime
    response_delay: float | None
    emotion_vector: dict[str, float]
    response_emotion_vector: dict[str, float] | None


class ChatroomMetadata(BaseModel):
    users: list[SingleUserData]
    threads: list[SingleThreadData]
    warnings: list[ChatWarningCandidate]
    start_time: datetime.datetime
    end_time: datetime.datetime

class UserAnalysis(BaseModel):
    username: str
    personality: str | None
    analysis: str
    potential_issues: str

class ChatroomReport(BaseModel):
    summary: str
    user_analysis: list[UserAnalysis]
    warning_1: ChatWarning
    warning_2: ChatWarning
    warning_3: ChatWarning

    def __str__(self):
        return f"""
# Chatroom Report
{self.summary}
## User Analysis
{self.user_analysis}
## Warning Analysis
{self.warning_1.__str__() + self.warning_2.__str__() + self.warning_3.__str__()}
        """
class NextMessageSuggestion(BaseModel):
    original_message: str
    suggested_message: str
    reason: str

class NextMessageSuggestions(BaseModel):
    suggestions: list[NextMessageSuggestion]

class GoogleWrapper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)

    def generate(
        self,
        model_name: str = "gemini-2.0-flash",
        prompt: str = "",
        structure: BaseModel = None,
        temperature: float = 0.2,
        tools: list = [],
    ):
        if not structure:
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    tools=tools,
                ),
            )
            return response.text
        else:
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    tools=tools,
                    response_mime_type="application/json",
                    response_schema=structure,
                ),
            )
            return response.parsed


class ChatroomReportAgent:
    def __init__(self, api_key: str, chatroom: Chatroom):
        self.chatroom = chatroom
        self.wrapper = GoogleWrapper(api_key=api_key)
        embedding_model_name = "upskyy/bge-m3-korean"
        embedding_cache_dir = "./models/bge-m3"
        self.embedding_model = SentenceTransformer(
            embedding_model_name, cache_folder=embedding_cache_dir
        )

    def get_all_msg_log(self) -> QuerySet[Message]:
        return Message.objects.filter(room=self.chatroom.id).order_by("sent_time")

    def get_all_threads(self) -> QuerySet[Thread]:
        return Thread.objects.filter(room=self.chatroom.id)

    def get_prev_msg_in_thread(self, message: Message, user: User) -> Message | None:
        return (
            Message.objects.filter(
                thread=message.thread, sent_time__lt=message.sent_time
            )
            .exclude(user_id=user.id)
            .order_by("-sent_time")
            .first()
        )

    def get_next_msg_in_thread(self, message: Message, user: User) -> Message | None:
        return (
            Message.objects.filter(
                thread=message.thread, sent_time__gt=message.sent_time
            )
            .exclude(user_id=user.id)
            .order_by("sent_time")
            .first()
        )

    def get_all_users(self) -> QuerySet[User]:
        user_ids = ChatroomUser.objects.filter(chatroom=self.chatroom.id).values_list(
            "user_id", flat=True
        )
        return User.objects.filter(id__in=user_ids)

    def generate_data(self) -> ChatroomMetadata:
        users = [self.generate_user_metadata(user) for user in self.get_all_users()]
        threads = sorted(
            [
                self.generate_thread_metadata(thread)
                for thread in self.get_all_threads()
            ],
            key=lambda x: x.start_time,
        )
        msgs = self.get_all_msg_log()
        start_time = msgs[0].sent_time if msgs else None
        end_time = msgs[len(msgs) - 1].sent_time if msgs else None
        return ChatroomMetadata(
            users=users,
            threads=threads,
            warnings=self.find_warning_candidates(msgs, users),
            start_time=start_time,
            end_time=end_time,
        )

    def find_warning_candidates(
        self, messages: QuerySet[Message], users: list[SingleUserData]
    ) -> list[ChatWarningCandidate]:
        warnings = []
        user_to_median_response = {
            user.user_id: user.median_response_time
            for user in users
            if user.median_response_time is not None
        }
        for msg in messages:
            next_message = self.get_next_msg_in_thread(msg, msg.user)
            response_delay = (
                (next_message.sent_time - msg.sent_time).total_seconds() / 60.0
                if next_message
                else None
            )
            median_response = user_to_median_response.get(next_message.user.id, None) if next_message else None

            response_emotion_vector = (
                next_message.metadata.get("emotions", []) if next_message else None
            )
            emotion_vector={
                emo["emotion"]: emo["score"] for emo in msg.metadata.get("emotions", [])
            }

            response_emotion_vector=(
                {
                    emo["emotion"]: emo["score"]
                    for emo in response_emotion_vector
                }
                if response_emotion_vector
                else None
            )

            if self.warn(
                response_delay, emotion_vector, response_emotion_vector, median_response
            ):
                warnings.append(
                    ChatWarningCandidate(
                        message=msg.content,
                        user_id=msg.user.id,
                        sent_time=msg.sent_time,
                        response_delay=response_delay,
                        emotion_vector=emotion_vector,
                        response_emotion_vector = response_emotion_vector,
                    )
                )

        return warnings

    def warn(
        self,
        response_delay: float | None,
        emotion_vector: list[dict],
        response_emotion_vector: list[dict] | None,
        median_response: int,
    ) -> bool:
        if (
            response_delay is None
            or response_emotion_vector is None
            or median_response is None
        ):
            return False

        score = 0

        if response_delay > median_response * 1.5:
            score += 1

        if (
            emotion_vector["anger"]
            + emotion_vector["sadness"]
            + emotion_vector["fear"]
            + emotion_vector["disgust"]
            > 0.5
        ):
            score += 1

        if (
            response_emotion_vector["anger"]
            + response_emotion_vector["sadness"]
            + response_emotion_vector["fear"]
            + response_emotion_vector["disgust"]
            > 0.5
        ):
            score += 1

        return score >= 2

    def generate_thread_user(self, user: User, thread: Thread) -> ThreadUserData:
        messages = Message.objects.filter(thread=thread.id, user_id=user.id)
        message_count = len(messages)
        if message_count == 0:
            return None

        avg_emotions = dict()
        avg_indices = dict()

        for msg in messages:
            for emo in msg.metadata.get("emotions", []):
                if emo["emotion"] not in avg_emotions:
                    avg_emotions[emo["emotion"]] = 0
                avg_emotions[emo["emotion"]] += emo["score"]

            for idx in msg.metadata.get("indices", []):
                if idx["index"] not in avg_indices:
                    avg_indices[idx["index"]] = 0
                avg_indices[idx["index"]] += idx["score"]

        avg_emotions = (
            {k: round(v / message_count, 2) for k, v in avg_emotions.items()}
            if message_count
            else {}
        )
        avg_indices = (
            {k: round(v / message_count, 2) for k, v in avg_indices.items()}
            if message_count
            else {}
        )

        return ThreadUserData(
            thread_id=thread.id,
            user_id=user.id,
            num_messages=message_count,
            avg_emotions=avg_emotions,
            avg_indices=avg_indices,
            start_time=messages[0].sent_time,
        )

    def generate_user_metadata(self, user: User) -> SingleUserData:
        total_threads = self.get_all_threads()
        total_thread_count = len(total_threads)

        if total_thread_count == 0:
            return None

        messages = Message.objects.filter(
            room=self.chatroom.id, user_id=user.id
        ).order_by("sent_time")
        message_count = len(messages)
        if message_count == 0:
            return None
        response_times = []
        initiative_count = 0
        length_sum = 0

        avg_emotions = dict()
        avg_indices = dict()

        for msg in messages:
            prev_msg = self.get_prev_msg_in_thread(msg, user)
            if prev_msg:
                response_times.append(
                    (msg.sent_time - prev_msg.sent_time).total_seconds() / 60.0
                )
            initiative_count += (
                not Message.objects.filter(
                    thread=msg.thread, sent_time__lt=msg.sent_time
                )
                .exclude(user_id=user.id)
                .exists()
            )
            length_sum += len(msg.content or "")

            for emo in msg.metadata.get("emotions", []):
                if emo["emotion"] not in avg_emotions:
                    avg_emotions[emo["emotion"]] = 0
                avg_emotions[emo["emotion"]] += emo["score"]

            for idx in msg.metadata.get("indices", []):
                if idx["index"] not in avg_indices:
                    avg_indices[idx["index"]] = 0
                avg_indices[idx["index"]] += idx["score"]

        return SingleUserData(
            user_id=user.id,
            username=user.name,
            personality=user.metadata.get("personality") if user.metadata else None,
            num_messages=Message.objects.filter(
                room=self.chatroom.id, user_id=user.id
            ).count(),
            initiative_rate=round(initiative_count / total_thread_count, 2),
            avg_msg_length=round(length_sum / message_count, 2),
            median_response_time=(
                round(sorted(response_times)[len(response_times) // 2], 2)
                if response_times
                else None
            ),
            avg_indices={
                k: round(v / message_count, 2) for k, v in avg_indices.items()
            },
            avg_emotions={
                k: round(v / message_count, 2) for k, v in avg_emotions.items()
            },
            thread_data=sorted(
                [self.generate_thread_user(user, thread) for thread in total_threads if isinstance(self.generate_thread_user(user, thread), ThreadUserData)],
                key=lambda x: x.start_time,
            ),
        )

    def generate_thread_metadata(self, thread: Thread) -> SingleThreadData:
        messages = Message.objects.filter(thread=thread.id).order_by("sent_time")
        message_count = len(messages)
        if message_count == 0:
            return None

        avg_emotions = dict()
        start_time = messages[0].sent_time
        end_time = messages[len(messages) - 1].sent_time

        for msg in messages:
            for emo in msg.metadata.get("emotions", []):
                if emo["emotion"] not in avg_emotions:
                    avg_emotions[emo["emotion"]] = 0
                avg_emotions[emo["emotion"]] += emo["score"]

        avg_emotions = (
            {k: round(v / message_count, 2) for k, v in avg_emotions.items()}
            if message_count
            else {}
        )

        topic_summary = thread.topic_summary or ""
        topic_embedding = self.embedding_model.encode([topic_summary])[0]

        # vector search : top 3 messages most similar to the topic summary
        top_messages = (
            messages.annotate(
                similarity=1 - CosineDistance(F("embedding"), topic_embedding)
            )
            .order_by("-similarity")
            .values_list("id", flat=True)
        )[:3]

        start_time = messages[0].sent_time if messages else None
        end_time = messages[len(messages) - 1].sent_time if messages else None

        return SingleThreadData(
            thread_id=thread.id,
            topic_summary=topic_summary,
            chat_type=(
                thread.metadata.get("chat_type")
                if thread.metadata
                else "Information Exchange"
            ),
            num_messages=message_count,
            avg_emotions=avg_emotions,
            key_messages=top_messages,
            duration_minutes=round((end_time - start_time).total_seconds() / 60.0, 2),
            start_time=start_time,
            end_time=end_time,
        )

    def generate_chatroom_report(self):
        metadata = self.generate_data()

        threads = [
            thread.model_dump(exclude="key_messages") for thread in metadata.threads
        ]
        users = [user.model_dump(exclude="thread_data") for user in metadata.users]
        warnings = [warning.model_dump() for warning in metadata.warnings]

        report = self.wrapper.generate(
            prompt=dedent(
                f"""
            <Role>
            You are a professional text analyst with a psychology background.
            </Role>

            Generate a chatroom report based on the following data.
            <Input>
            Users: { users }
            Threads: { threads }
            Warning Candidates : { warnings }
            </Input>

            <Task>
            1. Generate a summary and analysis of the main threads.
            2. Generate a user profile for each user based on their texting style and personality type.
            3. Identify three critical misunderstandings or conflicts in the chatroom from the warning candidates and provide analysis and suggestions for resolution.
            </Task>

            <Rules>
            1. Make sure the output is in Korean.
            </Rules>
            """
            ),
            structure=ChatroomReport,
        )

        beautified_report = self.wrapper.generate(
            prompt=dedent(
                f"""
            <Role>
            You are a text editor, enhancing raw text into readable and engaging content.
            </Role>

            <Task>
            Refine the following raw chatroom report into a polished and engaging format.
            Use clear headings, bullet points, tables where appropriate, and ensure the language is professional yet accessible.
            Make sure to use Markdown format.
            Organize the warnings into a markdown table.
            </Task>

            <Input>
            {report.__str__()}
            </Input>
            
            <Rules>
            Make sure the output is in Korean.
            </Rules>
            """
            )
        )
        with open("chatroom_report.md", "w", encoding="utf-8") as f:
            f.write(beautified_report)
        breakpoint()


class UserReportAgent:
    def __init__(self, api_key: str, user: User):
        self.user = user
        self.wrapper = GoogleWrapper(api_key=api_key)
        self.okt = Okt()

        self.keep_tags = [
            "Noun",
            "Verb",
            "Adjective",
        ]

    def get_all_msg_log(self) -> QuerySet[Message]:
        return Message.objects.filter(user_id=self.user.id).order_by("sent_time")

    def get_prev_msg_in_thread(self, message: Message) -> Message | None:
        return (
            Message.objects.filter(
                thread=message.thread, sent_time__lt=message.sent_time
            )
            .exclude(user_id=self.user.id)
            .order_by("-sent_time")
            .first()
        )

    def check_initiative(self, message: Message) -> bool:
        return not Message.objects.filter(
            thread=message.thread, sent_time__lt=message.sent_time
        ).exists()

    def generate_data(self):
        frequently_used_words = Counter()
        messages = self.get_all_msg_log()

        message_count = len(messages)
        chatroom_count = len(set(msg.room_id for msg in messages))
        thread_count = len(set(msg.thread_id for msg in messages if msg.thread_id))

        response_times = []
        initiative_count = 0

        sentence_count = 0
        length_sum = 0

        index_avg = dict()
        emotion_avg = dict()

        emoji_count = 0

        pos_tags = dict()

        for msg in messages:
            prev_msg = self.get_prev_msg_in_thread(msg)

            pos = self.okt.pos(msg.content, stem=True)
            emoji_count += msg.metadata.get("emoji_count", 0)

            filtered = Counter(word for word, tag in pos if tag in self.keep_tags)
            frequently_used_words.update(filtered)

            if prev_msg:
                response_times.append(
                    (msg.sent_time - prev_msg.sent_time).total_seconds() / 60.0
                )

            initiative_count += self.check_initiative(msg)
            for idx in msg.metadata.get("indices", []):
                if idx["index"] not in index_avg:
                    index_avg[idx["index"]] = 0
                index_avg[idx["index"]] += idx["score"]

            for emo in msg.metadata.get("emotions", []):
                if emo["emotion"] not in emotion_avg:
                    emotion_avg[emo["emotion"]] = 0
                emotion_avg[emo["emotion"]] += emo["score"]

            pos_tags_in_msg = msg.metadata.get("pos_tags", {})
            for tag, count in pos_tags_in_msg.items():
                if tag not in pos_tags:
                    pos_tags[tag] = 0
                pos_tags[tag] += count

            sentence_count += msg.metadata.get("num_sentences", 0)
            length_sum += len(msg.content or "")

        response_time_median = (
            round(sorted(response_times)[len(response_times) // 2], 2)
            if response_times
            else None
        )
        index_avg = {k: round(v / message_count, 2) for k, v in index_avg.items()}
        emotion_avg = {k: round(v / message_count, 2) for k, v in emotion_avg.items()}
        initiative_rate = (
            round(initiative_count / thread_count, 2) if message_count else None
        )
        avg_sentence_count = (
            round(sentence_count / message_count, 2) if message_count else None
        )
        avg_msg_length = round(length_sum / message_count, 2) if message_count else None
        pos_tags = (
            {
                tagset[k]: round(v / message_count, 2)
                for k, v in sorted(
                    pos_tags.items(), key=lambda item: item[1], reverse=True
                )
            }
            if message_count
            else {}
        )
        emoji_avg = round(emoji_count / message_count, 2) if message_count else 0

        return UserMetadata(
            median_response_time=response_time_median,
            avg_msg_length=avg_msg_length,
            initiative_rate=initiative_rate,
            avg_indices=index_avg,
            avg_emotions=emotion_avg,
            pos_tags=pos_tags,
            frequently_used_words=dict(frequently_used_words.most_common(20)),
            message_count=message_count,
            chatroom_count=chatroom_count,
            thread_count=thread_count,
            emoji_avg=emoji_avg,
        )

    def generate_user_report(self):
        metadata = self.generate_data()

        report = self.wrapper.generate(
            prompt=dedent(
                f"""
            <Role>
            You are a professional text analyst with a psychology background.
            </Role>

            Generate a user report based on the following metadata: {metadata.model_dump()}

            <Task>
            1. Classify the user's personality type into one of the following categories: 표현형, 본능형, 지시형, 정밀형, 조화형, 공감형, 분석형, 중재형.
            2. Summarize the user's overall texting style in two sentences.
            3. List three strengths and three weaknesses of the user's texting style.
            4. Evaluate the clarity of the user's sentences as 높음, 보통, or 낮음.
            5. Provide three specific and actionable action plans for the user to improve their texting style.
            </Task>
            
            For the personality type analysis, consider the following:

            1. Expressive : Direct, Emotional, Friendly, Dominant
                - 솔직하고 따뜻한 감정표현, 속도가 빠르고 에너지 높음.
                - 감탄사·이모지 ↑, 단문 직진형, “너무 좋다!!!”
            2. Instinctive : Direct, Emotional, Unfriendly, Dominant
                - 즉흥적 감정·불만 표현이 빠름. 선의여도 날카롭게 들릴 수 있음.
                - 명령·단정 “그건 아니야”, 반문·강조표현 ↑
            3. Commander : Direct, Logical, Dominant
                - 목표·효율 중심, 과업지향. 메시지 구조 선명.
                - “우선 A→B”, “데드라인”, 조건·절차·숫자 ↑
            4. Precisor : Direct, Logical, Neutral, Dominant
                - 팩트·정밀도 중시, 예외·세부조건을 명시.
                - “정확히”, “구체적으로”, “예외적으로” 등 세부 규정 ↑
            5. Harmonizer : Soft, Emotional, Friendly, Not-Dominant
                - 갈등 회피·관계 우선. 공감·배려 표현 풍부.
                - “혹시”, “괜찮다면”, “고마워/미안” ↑, 이모지 ↑
            6. Empathizer : Soft, Emotional, Friendly
                - 감정 읽기·언어 완충 탁월, 분위기 살림.
                - 반영문(“네 입장 이해”), 정서 라벨링(“답답했겠다”)
            7. Analyst : Soft, Logical Neutral, Not-Dominant
                - 데이터·근거 기반, 말투는 부드럽게.
                - “근거는…”, “데이터상”, 완곡+논리 접속사 동시 ↑
            8. Mediator : Soft, Logical, Friendly
                - 갈등 중재·프레이밍 능숙, 합의안 제시.
                - “한편/다만”, “둘 다 맞음”, “중간 제안” ↑
            

            <Rules>
            1. Generate the report in Korean.
            2. Ensure the report is concise and clear.
            3. Use bullet points for strengths, weaknesses, and action plans.
            </Rules>
            """
            ),
            temperature=0.3,
            structure=UserReport,
        )

        with open("user_report.txt", "w", encoding="utf-8") as f:
            f.write(metadata.__str__() + "=" * 20 + report.__str__())

        self.user.metadata = {
            "personality": report.user_type,
        }
        self.user.save()
        return metadata


class NextMessageEditAgent:
    def __init__(self, api_key: str):
        self.wrapper = GoogleWrapper(api_key=api_key)
    
    def get_msg(self, thread: Thread) -> Message:
        return Message.objects.filter(thread=thread.id).order_by('-sent_time').first()
    
    def suggest_message(self, chatroom: Chatroom, user: User, message: str):

        threads = Thread.objects.filter(room=chatroom.id)
        latest_thread = sorted(threads, key=lambda x: self.get_msg(x).sent_time, reverse=True)[0] if threads else None
        users = User.objects.filter(id__in=ChatroomUser.objects.filter(chatroom=chatroom.id).values_list("user_id", flat=True))
        other_user = users.exclude(id=user.id)[0]

        other_personality = other_user.metadata.get("personality") if other_user.metadata else None
        curr_personality = user.metadata.get("personality") if user.metadata else None

        prompt = dedent(
            f"""
        <Role>
        You are a professional text analyst with a psychology background.
        </Role>
        Given the current chatroom situation, suggest an three appropriate alternate message suggestions for the user considering their personality type and the personality type of the other participant.

        <Input>
        Current User: {user.name} (Personality: {curr_personality})
        Recipient User: {other_user.name} (Personality: {other_personality})
        Latest Thread Topic: {latest_thread.topic_summary if latest_thread else "N/A"}
        Current Message: {message}
        </Input>

        <Previous Message Log>
        { ' '.join(Message.objects.filter(thread=latest_thread.id).order_by('-sent_time').values_list('content', flat=True)[:5]) if latest_thread else "N/A" }
        </Previous Message Log>

        <Task>
        1. Analyze the current message and the personalities of both users.
        2. Suggest three alternate message options instead of the one given that aligns with the current user's personality type while considering the recipient's personality type.
        3. Minimize the risk of misunderstandings or conflicts based on personality differences.
        </Task>

        <Output Format>
        {{
            "suggested_message": str
        }}
        """)

        response = self.wrapper.generate(prompt=prompt, structure=NextMessageSuggestions)
        breakpoint()
        return response


if __name__ == "__main__":
    pass
