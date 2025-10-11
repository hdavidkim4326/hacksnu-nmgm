from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from konlpy.tag import Kkma
from nmgm.models import Message, Thread
from datetime import timedelta

embedding_model_name = "upskyy/bge-m3-korean"
embedding_cache_dir = "./models/bge-m3"

tagging_model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
tagging_cache_dir = "./models/mDeBERTa-v3-base-mnli-xnli"

nli_model_name = "roberta-large-mnli"
nli_cachee_dir = "./models/roberta-large-mnli"

"""
STEP 0 : preprocess all messages in chatrooms (message grouping, embeddings, metadata etc)
STEP 1 : cut chatroom into multiple threads (time, topic)
STEP 2 : generate chatroom analysis based on threads and topic
STEP 3 : generate user analysis based on chatroom data
STEP 4 : generate message edit features
"""

@dataclass
class MessageMetadata:
    pos_tags: dict
    information_measure: float
    emoji_count: int
    emotion_vector: dict
    ending_morphemes: list
    readability_measure: dict
    message_type: str


@dataclass
class ThreadMetadata:
    topic_summary: str
    chat_type: str


class ChatroomProcessor:
    def __init__(self, chatroom, create_pipeline = False):
        self.chatroom = chatroom

        self.embedding_model = SentenceTransformer(
                embedding_model_name, cache_folder=embedding_cache_dir
            )
        self.konlp = Kkma()
        
        if create_pipeline:
            self.relatedness_classifier = pipeline(
                "text-classification",
                model="./models/mDeBERTa-v3-base-mnli-xnli", 
            )
        
    
    def relatedness(self, msg1, msg2) -> bool:
        result = self.relatedness_classifier(
            [msg1 + " " + msg2],
        )
        return result[0]["label"] != "neutral"

    def pipeline(self):
        self.embed()
        self.assign_threads()

    def embed(self):
        messages = Message.objects.filter(room=self.chatroom, embedding__isnull=True)
        embeddings = self.embedding_model.encode(
            [msg.content for msg in messages], batch_size=32, show_progress_bar=True
        )
        for msg, emb in zip(messages, embeddings):
            msg.embedding = emb
            msg.save()

    def clear_threads(self):
        Message.objects.filter(room=self.chatroom).update(thread=None)
        Thread.objects.filter(room=self.chatroom).delete()

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
                if (
                    message.sent_time - prev_msg.sent_time < timedelta(minutes=30)
                    or self.relatedness(prev_msg.content, message.content) # 전부 연관 있다고 해버리네;; 역치를 높여야 할 듯
                ):
                    message.thread = curr_thread
                    message.save()
                else:
                    curr_thread = Thread(room=self.chatroom)
                    message.thread = curr_thread
                    curr_thread.save()
                    message.save()
            prev_msg = message

        # for thread in Thread.objects.filter(room=self.chatroom, topic_summary__isnull=True):
        #     self.generate_thread_metadata(thread)
