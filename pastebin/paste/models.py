from django.db import models
from django.contrib.auth.models import User


class Paste(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pastes',
        blank=True,
        null=True
    )
    hash = models.CharField(max_length=10)
    expiration_type = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hash


