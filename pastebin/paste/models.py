from django.db import models


class Paste(models.Model):
    hash = models.CharField(max_length=10)
    s3_key = models.CharField()

    def __str__(self):
        return self.s3_key


class SimpleText(models.Model):
    id = models.ForeignKey
    text = models.CharField()
