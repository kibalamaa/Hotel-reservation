from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('new', 'New'), ('delivered', 'Delivered')],
        default='new'
    )

    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username}: {self.message[:30]}"
    
    