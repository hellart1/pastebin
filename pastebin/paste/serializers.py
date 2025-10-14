from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from .models import Paste


# class PasteModel:
#     def __init__(self, title, content):
#         self.title = title
#         self.content = content


class PasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paste
        fields = ('hash', 'url')


# def encode():
#     model = PasteModel('Pune', 'pude')
#     model_sr = PasteSerializer(model)
#     print(model_sr.data)
#     json = JSONRenderer().render(model_sr.data)
#     print(json)
#
# def decode():
#     pass


# class PasteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Paste
#         fields = ('hash',)
