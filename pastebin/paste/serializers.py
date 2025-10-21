from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from .models import Paste


class PasteSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Paste
        fields = ('hash', 'expiration_type', 'download_url')

    def get_download_url(self, obj):
        return self.context.get('download_url')
