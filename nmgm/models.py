from django.db import models
from pgvector.django import VectorField

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    metadata = models.JSONField(null=True)

    def __str__(self):
        return self.username

class Chatroom(models.Model):
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True)

    def __str__ (self):
        return self.name

class ChatroomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)

class Thread(models.Model):
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    topic_summary = models.TextField(null = True)
    metadata = models.JSONField(null=True)
    
    def generate_metadata(self):
        self.topic_summary = self.summarize_topic()
        self.chat_type = self.classify_chat_type() # 의사결정, 감정공유, 갈등조율, 정보교환, 사담/농담
        self.save()


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
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