# nmgm/models.py

from django.db import models
from pgvector.django import VectorField
from datetime import datetime
from django.utils import timezone

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=150, unique=True)
    # email = models.EmailField(unique=True)
    metadata = models.JSONField(null=True)

    def __str__(self):
        return self.username


class Chatroom(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True)

    def __str__(self):
        return self.name

    def load(self, dataframe):
        for _, row in dataframe.iterrows():
            # user, _ = User.objects.get_or_create(name=row["보낸 사람"])
            # ChatroomUser.objects.get_or_create(user=user, chatroom=self)

            # dt_str = f"{row['날짜']} {row['시간']}"
            # # Example: "2025.06.10 9:42"
            # naive_dt = datetime.strptime(dt_str, "%Y.%m.%d %H:%M")
            # aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())

            # Message.objects.create(
            #     user=user,
            #     room=self,
            #     content=row["내용"],
            #     sent_time=aware_dt,
            # )
            user, _ = User.objects.get_or_create(name=row["User"])
            ChatroomUser.objects.get_or_create(user=user, chatroom=self)

            dt_str = row['Date']
            # Example: "2025-06-10 09:42:00"
            naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
            Message.objects.create(
                user=user,
                room=self,
                content=row["Message"],
                sent_time=aware_dt,
            )


class ChatroomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)


class Thread(models.Model):
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    topic_summary = models.TextField(null=True)
    metadata = models.JSONField(null=True)


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
    related_message = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    content = models.TextField()
    sent_time = models.DateTimeField(auto_now_add=False)
    metadata = models.JSONField(null=True)
    embedding = VectorField(null=True, dimensions=1024)

    def __str__(self):
        return (
            f"By: {self.user.name}, sent on: {self.sent_time}, content: {self.content}"
        )
