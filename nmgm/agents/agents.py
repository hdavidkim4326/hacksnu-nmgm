from .wrappers import GoogleWrapper
from konlpy.tag import Okt
from django.db.models import QuerySet
from nmgm.models import Message, Thread
from datetime import datetime, timedelta
from tqdm import tqdm
import re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from ..models import Chatroom, User, Message, Thread, ChatroomUser
from .prompts import (
    related_prompt,
    msg_analysis_prompt,
    thread_analysis_prompt,
    next_message_prompt,
    user_report_prompt,
    summarize_all_threads_prompt,
    describe_personality_prompt,
    chatroom_report_prompt,
)
import emoji
from collections import Counter

from .types import (
    IsRelated,
    PosTag,
    WordCount,
    MsgMetadata,
    ThreadMetadata,
    NextMessageEdit,
    UserReport,
    ChatroomReport,
    SentenceClarity,
    ChatSummary,
    UserAnalysis,
    ChatWarningCandidate,
    ThreadInfo,
    BriefMessageInfo
)

# okt = Okt()
# tagset = okt.tagset

load_dotenv()

KEEP_TAGS = {
    "Noun",
    "Verb",
    "Adjective"
}


class BaseAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.wrapper = GoogleWrapper(api_key=api_key)

class ReportAgent(BaseAgent):
    def __init__ (self, api_key: str, user: User = None, chatroom: Chatroom = None):
        super().__init__(api_key)
        if chatroom:
            self.chatroom = chatroom
            self.user = None
        elif user:
            self.user = user
            self.chatroom = None
        else:
            raise ValueError("Either user or chatroom must be provided")
    
    def get_all_msg_log(self) -> list[Message]:
        if self.chatroom:
            return Message.objects.filter(room=self.chatroom.id).order_by("sent_time")
        else:
            return Message.objects.filter(user_id=self.user.id).order_by("sent_time")
    
    def get_prev_msg_in_thread(self, message: Message) -> Message | None:
        return (
            Message.objects.filter(
                thread=message.thread, sent_time__lt=message.sent_time
            )
            .exclude(user_id=message.user_id)
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
    
    def check_initiative(self, message: Message) -> bool:
        return not Message.objects.filter(
            thread=message.thread, sent_time__lt=message.sent_time
        ).exists()

class Loader(BaseAgent):
    def __init__ (self, api_key: str, chatroom: Chatroom):
        super().__init__(api_key)
        self.chatroom = chatroom
        # self.embedding_model = SentenceTransformer(
        #     "upskyy/bge-m3-korean", cache_folder="./models/bge-m3"
        # )
        # self.konlp = Okt()
    
    def load_chatroom(self):
        # self.embed_all_messages()
        self.assign_threads()
        self.generate_message_metadata()
        self.generate_thread_metadata()
    
    # def embed_all_messages(self):
    #     messages = Message.objects.filter(room=self.chatroom, embedding__isnull=True)
    #     embeddings = self.embedding_model.encode(
    #         [msg.content for msg in messages], batch_size=32, show_progress_bar=True
    #     )
    #     for msg, emb in zip(messages, embeddings):
    #         msg.embedding = emb
    #         msg.save()
    
    def assign_threads(self):
        untagged_messages = Message.objects.filter(
            room=self.chatroom, thread__isnull=True
        ).order_by("sent_time")

        prev_msg = (
            Message.objects.filter(room=self.chatroom, thread__isnull=False)
            .order_by("-sent_time")
            .first()
            if Message.objects.filter(room=self.chatroom, thread__isnull=False).exists()
            else None
        )
        curr_thread = prev_msg.thread if prev_msg and prev_msg.thread else None

        for message in untagged_messages:
            if not curr_thread:  # no current thread
                curr_thread = Thread(room=self.chatroom)
                message.thread = curr_thread
                curr_thread.save()
                message.save()
            else:
                if message.sent_time - prev_msg.sent_time <= timedelta(
                    minutes=30
                ) or self.check_relatedness(
                    prev_msg.content, message.content
                ):
                    message.thread = curr_thread
                    message.save()
                else:
                    curr_thread = Thread(room=self.chatroom)
                    message.thread = curr_thread
                    curr_thread.save()
                    message.save()
            prev_msg = message

    def generate_message_metadata(self):
        messages = Message.objects.filter(
            room=self.chatroom, metadata__isnull=True
        ).order_by("sent_time")

        for msg in tqdm(messages):
            # EMOJI COUNT
            emoji_count = len([ch for ch in msg.content if ch in emoji.EMOJI_DATA])

            # POS TAGGING
            if isinstance(msg.content, bytes):
                msg.content = msg.content.decode("utf-8", errors="ignore")
            safe_text = re.sub(r"[^가-힣A-Za-z0-9\s.,!?~]", "", msg.content or "")
            # pos_tags = self.konlp.pos(safe_text)
            pos_dict = {}
            
            # for _, tag in pos_tags:
            #     if tag not in pos_dict:
            #         pos_dict[tag] = 0
            #     pos_dict[tag] += 1

            # EMOTION ANALYSIS (Gemini)
            msg_metadata = self.analyze_message(msg.content).model_dump()
            msg_metadata["freq_words"] = {}#Counter(word for word, tag in pos_tags if tag in KEEP_TAGS)
            msg_metadata["emoji_count"] = emoji_count
            msg_metadata["pos_tags"] = pos_dict

            msg.metadata = msg_metadata
            msg.save()
    
    def generate_thread_metadata(self):
        threads = Thread.objects.filter(room=self.chatroom, topic_summary__isnull=True)
        for thread in tqdm(threads):
            messages = list(Message.objects.filter(thread=thread).order_by("sent_time"))
            if len(messages) == 0:
                continue

            result = self.summarize_thread(
                [msg.__str__() for msg in messages]
            )
            thread.topic_summary = result.topic_summary
            thread.metadata = {
                "chat_type": result.chat_type,
                "start_time": messages[0].sent_time.isoformat(),
                "end_time": messages[len(messages)-1].sent_time.isoformat(),
            }
            thread.save()

    def check_relatedness(self, msg1: str, msg2: str) -> bool:
        result: IsRelated = self.wrapper.generate(
            model_name="gemini-2.0-flash",
            prompt=related_prompt.format(msg1=msg1, msg2=msg2),
            structure=IsRelated,
            temperature=0.2,
        )
        return result.related
    
    def analyze_message (self, msg: str) -> MsgMetadata:
        result: MsgMetadata = self.wrapper.generate(
            model_name="gemini-2.0-flash",
            prompt=msg_analysis_prompt.format(message=msg),
            structure=MsgMetadata,
            temperature=0.2,
        )
        return result
    
    def summarize_thread (self, messages: list[str]) -> ThreadMetadata:
        result: ThreadMetadata = self.wrapper.generate(
            model_name="gemini-2.0-flash",
            prompt=thread_analysis_prompt.format(messages="\n".join(messages)),
            structure=ThreadMetadata,
            temperature=0.2,
        )
        return result

    def clear_threads(self):
        Message.objects.filter(room=self.chatroom).update(thread=None)
        Thread.objects.filter(room=self.chatroom).delete()

    def clear_msg_metadata(self):
        messages = Message.objects.filter(room=self.chatroom)
        for msg in messages:
            msg.metadata = None
            msg.save()

class MessageEditor(BaseAgent):
    def suggest_message(self, chatroom: Chatroom, user: User, message: str) -> str:
        threads = Thread.objects.filter(room=chatroom.id)
        latest_thread = sorted(threads, key = lambda x: x.metadata.get("end_time") if x.metadata else "")[-1] if threads else None

        users = User.objects.filter(id__in=ChatroomUser.objects.filter(chatroom=chatroom.id).values_list("user_id", flat=True))
        
        other_user = users.exclude(id=user.id)[0]
        other_personality = other_user.metadata.get("personality") if other_user.metadata else None
        curr_personality = user.metadata.get("personality") if user.metadata else None

        response : NextMessageEdit = self.wrapper.generate(
            prompt = next_message_prompt.format(
                username=user.name,
                curr_personality=curr_personality or "N/A",
                other_username=other_user.name,
                other_personality=other_personality or "N/A",
                latest_thread=latest_thread,
                message=message,
                message_log="\n".join(msg.__str__() for msg in Message.objects.filter(room=chatroom).order_by("-sent_time"))
            ),
            model_name="gemini-2.0-flash",
            structure= NextMessageEdit,
        )

        return response.model_dump()

class UserReportAgent(ReportAgent):
    def __init__ (self, api_key: str, user: User, chatroom: Chatroom = None):
        super().__init__(api_key, user=user, chatroom=None)

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
            if prev_msg:
                response_times.append(
                    (msg.sent_time - prev_msg.sent_time).total_seconds() / 60.0
                )
            
            emoji_count += msg.metadata.get("emoji_count", 0)
            frequently_used_words.update(msg.metadata.get("freq_words", {}))

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
        avg_msg_length = round(length_sum / message_count, 2) if message_count else None
        pos_tags = []
        # pos_tags = [
        #     {
        #         tagset[k]: round(v / message_count, 2)
        #     } for k, v in sorted(
        #             pos_tags.items(), key=lambda item: item[1], reverse=True
        #         )
        # ] if message_count else []
        emoji_avg = round(emoji_count / message_count, 2) if message_count else 0

        user_report = UserReport(username=self.user.name,
                median_response_time=response_time_median or 0,
                avg_msg_length=avg_msg_length or 0,
                initiative_rate=initiative_rate or 0,
                message_count=message_count,
                chatroom_count=chatroom_count,
                thread_count=thread_count,
                emoji_avg=emoji_avg,
                pos_tags=[{"tag":k, "rate":v} for d in pos_tags for k, v in d.items()],
                word_counts=[
                    {"word": word, "count": count}
                    for word, count in frequently_used_words.most_common(20)
                ],
                avg_emotions=[
                    {"emotion": emo, "score": score}
                    for emo, score in emotion_avg.items()
                ],
                avg_indices=[
                    {"index": idx, "score": score}
                    for idx, score in index_avg.items()
                ],
                user_type=self.user.metadata.get("personality") if self.user.metadata else None,
                summary="",
                strengths=[],
                weaknesses=[],
                sentence_clarity=SentenceClarity.AVERAGE,
                action_plans=[]
            )
        return user_report
    
    def generate_report(self):
        report = self.generate_data()

        result : UserReport = self.wrapper.generate(
            prompt = user_report_prompt.format(
                metadata=report.model_dump_json()
            ),
            model_name="gemini-2.5-pro",
            structure= UserReport,
            temperature=0.3,
        )
        return result.model_dump_json()

class ChatroomReportAgent(ReportAgent):
    def __init__ (self, api_key: str, chatroom: Chatroom, user: User = None):
        super().__init__(api_key, user=None, chatroom=chatroom)

    def get_all_threads(self) -> list[Thread]:
        return Thread.objects.filter(room=self.chatroom.id)
    
    def get_all_users(self) -> QuerySet[User]:
        user_ids = ChatroomUser.objects.filter(chatroom=self.chatroom.id).values_list(
            "user_id", flat=True
        )
        return User.objects.filter(id__in=user_ids)
    
    def generate_data(self) -> ChatroomReport:
        chat_summary = self.get_chat_summary()
        user_analyses = [self.get_user_analysis(user) for user in self.get_all_users()]
        warning_candidates = self.get_warnings(self.get_all_msg_log(), user_analyses)
        chat_report = ChatroomReport(
            chatsummary=chat_summary,
            user_analysis=user_analyses,
            warnings=[],
        )
        return chat_report, warning_candidates
    
    def generate_report(self):
        report, warning_candidates = self.generate_data()
        result : ChatroomReport = self.wrapper.generate(
            prompt = chatroom_report_prompt.format(
                metadata=report.model_dump_json(),
                candidates = [wc.model_dump() for wc in warning_candidates]
            ),
            model_name="gemini-2.5-pro",
            structure= ChatroomReport,
            temperature=0.3,
        )
        return result.model_dump_json()

    def get_chat_summary(self) -> ChatSummary:
        threads = self.get_all_threads()
        if not threads:
            return ChatSummary(
                summary="No messages in this chatroom.",
                start_time=None,
                end_time=None,
                threads=[],
            )
        
        start_time = min(thread.metadata.get("start_time") for thread in threads if thread.metadata and thread.metadata.get("start_time"))
        end_time = max(thread.metadata.get("end_time") for thread in threads if thread.metadata and thread.metadata.get("end_time"))

        summary = self.wrapper.generate(
            prompt=summarize_all_threads_prompt.format(
                messages = "\n".join(thread.topic_summary for thread in threads if thread.topic_summary)
            ),
            model_name="gemini-2.0-flash",
        )

        return ChatSummary(
            summary=summary,
            start_time=datetime.fromisoformat(start_time) if start_time else None,
            end_time=datetime.fromisoformat(end_time) if end_time else None,
            threads=[
                self.summarize_thread_info(thread)
                for thread in threads
            ],
        )

    def summarize_thread_info(self, thread: Thread) -> ThreadInfo:
        messages = Message.objects.filter(thread=thread).order_by("sent_time")
        if not messages:
            return ThreadInfo(
                topic_summary="No messages in this thread.",
                chat_type=None,
                num_messages=0,
                avg_emotions=[],
                duration=0.0,
            )
        
        start_time = messages[0].sent_time
        end_time = messages[len(messages)-1].sent_time
        duration = (end_time - start_time).total_seconds() / 60.0

        emotion_avg = dict()
        for msg in messages:
            for emo in msg.metadata.get("emotions", []):
                if emo["emotion"] not in emotion_avg:
                    emotion_avg[emo["emotion"]] = 0
                emotion_avg[emo["emotion"]] += emo["score"]
        emotion_avg = [
            {"emotion": emo, "score": round(score / len(messages), 2)}
            for emo, score in emotion_avg.items()
        ]

        return ThreadInfo(
            topic_summary=thread.topic_summary or "N/A",
            chat_type=thread.metadata.get("chat_type") if thread.metadata else None,
            num_messages=len(messages),
            avg_emotions=emotion_avg,
            duration=round(duration, 2),
        )
    
    def get_user_analysis(self, user: User) -> UserAnalysis:
        username = user.name
        personality = user.metadata.get("personality") if user.metadata else None
        messages = Message.objects.filter(room=self.chatroom, user_id=user.id).order_by("sent_time")

        if not messages:
            return UserAnalysis(
                username=username,
                personality=personality,
                description="No messages from this user.",
                avg_indices=[],
                avg_emotions=[],
                median_response_time=0.0,
                initiative_rate=0.0,
                messages=[],
            )
        response_times = []
        initiative_count = 0
        index_avg = dict()
        emotion_avg = dict()
        brief_messages = []

        for msg in messages:
            prev_msg = self.get_prev_msg_in_thread(msg)
            if prev_msg:
                response_times.append(
                    (msg.sent_time - prev_msg.sent_time).total_seconds() / 60.0
                )
            initiative_count += self.check_initiative(msg)
            for idx in msg.metadata.get("indices", []):
                if idx["index"] not in index_avg:
                    index_avg[idx["index"]] = 0
                index_avg[idx["index"]] += idx["score"]

            sentiment_score = 0

            for emo in msg.metadata.get("emotions", []):
                if emo["emotion"] not in emotion_avg:
                    emotion_avg[emo["emotion"]] = 0
                emotion_avg[emo["emotion"]] += emo["score"]
                if emo["emotion"] in ["joy", "surprise"]:
                    sentiment_score += emo["score"]
                else:
                    sentiment_score -= emo["score"]
            
            brief_messages.append(
                BriefMessageInfo(
                    sent_time=msg.sent_time,
                    sentiment=round(sentiment_score, 2),
                )
            )
        
        response_time_median = (
            round(sorted(response_times)[len(response_times) // 2], 2)
            if response_times
            else 0.0
        )
        index_avg = [
            {"index": idx, "score": round(score / len(messages), 2)}
            for idx, score in index_avg.items()
        ]
        emotion_avg = [
            {"emotion": emo, "score": round(score / len(messages), 2)}
            for emo, score in emotion_avg.items()
        ]
        initiative_rate = round(initiative_count / len(set(msg.thread_id for msg in messages if msg.thread_id)), 2) if messages else 0.0
        
        description = self.wrapper.generate(
            prompt = describe_personality_prompt.format(
                metadata = {
                    "username": username,
                    "personality": personality or "N/A",
                    "avg_indices": index_avg,
                    "avg_emotions": emotion_avg,
                    "median_response_time": response_time_median,
                    "initiative_rate": initiative_rate,
                }
            ),
            model_name="gemini-2.0-flash",
        )

        return UserAnalysis(
            username=username,
            personality=personality,
            description=description,
            avg_indices=index_avg,
            avg_emotions=emotion_avg,
            median_response_time=response_time_median,
            initiative_rate=initiative_rate,
            messages=brief_messages,
        )
    
    def get_warnings(
        self, messages: QuerySet[Message], users: list[UserAnalysis]
    ) -> list[ChatWarningCandidate]:
        warnings = []
        user_to_median_response = {
            user.username: user.median_response_time
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
                        user_id=msg.user_id,
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