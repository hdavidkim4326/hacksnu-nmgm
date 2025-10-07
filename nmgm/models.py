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
    topic_summary = models.TextField()

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
    related_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    content = models.TextField()
    sent_time = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True)
    embedding = VectorField(null=False, dimensions = 1024)

    def __str__(self):
        return f"Message {self.id} by {self.user.name} in {self.room.name}"

