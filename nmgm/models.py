from django.db import models
from pgvector.django import VectorField
<<<<<<< HEAD

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
=======
from datetime import datetime
from django.utils import timezone

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=150, unique=True)
    # email = models.EmailField(unique=True)
>>>>>>> 8136b315 ([add thread cut])
    metadata = models.JSONField(null=True)

    def __str__(self):
        return self.username

<<<<<<< HEAD
class Chatroom(models.Model):
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True)

    def __str__ (self):
        return self.name

=======

class Chatroom(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True)

    def __str__(self):
        return self.name

    def load(self, dataframe):
        for _, row in dataframe.iterrows():
            user, is_new = User.objects.get_or_create(name=row["보낸 사람"])

            if is_new:
                ChatroomUser.objects.get_or_create(user=user, chatroom=self)

            dt_str = f"{row['날짜']} {row['시간']}"
            # Example: "2025.06.10 9:42"
            naive_dt = datetime.strptime(dt_str, "%Y.%m.%d %H:%M")
            aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())

            Message.objects.create(
                user=user,
                room=self,
                content=row["내용"],
                sent_time=aware_dt,
            )


>>>>>>> 8136b315 ([add thread cut])
class ChatroomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)

<<<<<<< HEAD
class Thread(models.Model):
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    topic_summary = models.TextField(null = True)
    metadata = models.JSONField(null=True)
    
    def generate_metadata(self):
        self.topic_summary = self.summarize_topic()
        self.chat_type = self.classify_chat_type() # 의사결정, 감정공유, 갈등조율, 정보교환, 사담/농담
=======

class Thread(models.Model):
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    topic_summary = models.TextField(null=True)
    metadata = models.JSONField(null=True)

    def generate_metadata(self):
        self.topic_summary = self.summarize_topic()
        self.chat_type = (
            self.classify_chat_type()
        )  # 의사결정, 감정공유, 갈등조율, 정보교환, 사담/농담
>>>>>>> 8136b315 ([add thread cut])
        self.save()


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
<<<<<<< HEAD
    related_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    content = models.TextField()
    sent_time = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True)
    embedding = VectorField(null=True, dimensions = 1024)

    def __str__(self):
        return f"Message {self.id} by {self.user.name} in {self.room.name}"
    
    def generate_metadata(self):
        self.embeddings = self.embed() # generate embedding vector and store
        self.link_messages() # categorize message to thread and link related_message
        self.pos_tag() # pos_tagging - softening words, pronouns, connectives, intensifers
        self.information_measure() # information measure - how many sentences is this message? (perhaps 0.5, perhaps 2)
        self.count_emojis() # emoji count
        self.emotion_vector() # circumplex model : valence, arousal
        self.ending_morphemes() # sentence ending morphemes
        self.readability_measure() # readability measure : Flesch-Kincaid, Gunning Fog, SMOG, Coleman-Liau
        self.message_type() # question, response, link, attachment

        self.save()
=======
    related_message = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    content = models.TextField()
    sent_time = models.DateTimeField(auto_now_add=False)
    metadata = models.JSONField(null=True)
    embedding = VectorField(null=True, dimensions=1024)

    def __str__(self):
        return f"Message {self.id} by {self.user.name} in {self.room.name}"

    def generate_metadata(self):
        self.link_messages()  # categorize message to thread and link related_message

        self.pos_tag()  # pos_tagging - softening words, pronouns, connectives, intensifers
        self.information_measure()  # information measure - how many sentences is this message? (perhaps 0.5, perhaps 2)
        self.count_emojis()  # emoji count
        self.emotion_vector()  # circumplex model : valence, arousal
        self.ending_morphemes()  # sentence ending morphemes
        self.readability_measure()  # readability measure : Flesch-Kincaid, Gunning Fog, SMOG, Coleman-Liau
        self.message_type()  # question, response, link, attachment

        self.save()
>>>>>>> 8136b315 ([add thread cut])
