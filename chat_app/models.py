import uuid
from django.db import models

# Create your models here.


class MessageModel(models.Model):
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    message = models.TextField(verbose_name='Message', null=False)
    receiver_id = models.ForeignKey(
        to='Users.User', on_delete=models.CASCADE, null=False, related_name='receiver_id')
    sender_id = models.ForeignKey(
        to='Users.User', on_delete=models.CASCADE, null=False, related_name='sender_id')
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name='created_at')
    updated_at = models.DateTimeField(
        auto_now=True, null=True, verbose_name='updated_at')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Messages"
