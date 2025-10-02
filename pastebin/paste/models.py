from django.db import models


class Paste(models.Model):
    hash = models.CharField(max_length=10)
    url = models.URLField()

    def __str__(self):
        return self.hash

