import base64

import boto3
from .models import Paste
import random
from django.conf import settings
import os


def get_s3_resource():
    return boto3.resource(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )


def get_unique_hash():
    for attempts in range(100):
        random_bytes = os.urandom(10)
        coded_bytes = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        coded_bytes.replace('=', '')
        _hash = coded_bytes[:7]

        if not Paste.objects.filter(s3_key=_hash).exists():
            return _hash

    raise ValueError("Не удалось найти уникальный хэш. Повторите позже")

