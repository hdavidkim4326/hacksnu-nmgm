from dataclasses import dataclass

from konlpy.tag import Kkma
from nmgm.models import Message, Thread
from datetime import timedelta
from nmgm.agents import MsgAnalysisAgent
import os
import emoji
from tqdm import tqdm
import re
from dotenv import load_dotenv

load_dotenv()

embedding_model_name = "upskyy/bge-m3-korean"
embedding_cache_dir = "./models/bge-m3"

tagging_model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
tagging_cache_dir = "./models/mDeBERTa-v3-base-mnli-xnli"

emotion_model_name = "dlckdfuf141/korean-emotion-kluebert-v2"
emotion_cache_dir = "./models/korean-emotion-kluebert-v2"

"""
STEP 0 : preprocess all messages in chatrooms (message grouping, embeddings, metadata etc)
STEP 1 : cut chatroom into multiple threads (time, topic)
STEP 2 : generate chatroom analysis based on threads and topic
STEP 3 : generate user analysis based on chatroom data
STEP 4 : generate message edit features
"""


class ChatroomProcessor:
    def __init__(self, chatroom, thread_pipeline=False):
        self.chatroom = chatroom
        from sentence_transformers import SentenceTransformer

        self.embedding_model = SentenceTransformer(
            embedding_model_name, cache_folder=embedding_cache_dir
        )
        self.konlp = Kkma()
        self.msg_agent = MsgAnalysisAgent(os.getenv("GEMINI_KEY"))

    def relatedness(self, msg1, msg2) -> bool:
        result = self.relatedness_classifier(
            [msg1 + " " + msg2],
        )
        return result[0]["label"] != "neutral"

    def pipeline(self):
        # self.embed_all_messages()
        self.assign_threads()
        # self.generate_message_metadata()
        self.generate_thread_metadata()

    def embed_all_messages(self):
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

    def clear_emotions(self):
        messages = Message.objects.filter(room=self.chatroom)
        for msg in messages:
            metadata = msg.metadata or {}
            if "emotion_vector" in metadata:
                del metadata["emotion_vector"]
                msg.metadata = metadata
                msg.save()

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
                ) or self.msg_agent.judge_relatedness(
                    prev_msg.__str__(), message.__str__()
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
            pos_tags = self.konlp.pos(safe_text)
            pos_dict = {}
            for word, tag in pos_tags:
                if tag not in pos_dict:
                    pos_dict[tag] = 0
                pos_dict[tag] += 1

            # EMOTION ANALYSIS (Gemini)
            msg_metadata = self.msg_agent.analyze_message(msg.content).model_dump()
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

            result = self.msg_agent.summarize_thread(
                [msg.__str__() for msg in messages]
            )
            thread.topic_summary = result.topic_summary
            thread.metadata = {"chat_type": result.chat_type}
            thread.save()
