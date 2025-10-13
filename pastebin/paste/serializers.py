from rest_framework import serializers

from .models import Paste


class PasteModel:
    def __init__(self, title, content):
        self.title = title
        self.content = content


class PasteSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()

def encode():



# class PasteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Paste
#         fields = ('hash',)
