from django.db import models


class Paste(models.Model):
    hash = models.CharField(max_length=10)
    expiration_type = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hash

