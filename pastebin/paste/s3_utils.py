import base64

import boto3
from django.shortcuts import render, get_object_or_404, redirect

from .forms import TextForm
from .models import Paste
from django.conf import settings
import os
from datetime import datetime, timedelta


def s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
        region_name=os.getenv("ru-central1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )


def s3_resource():
    return boto3.resource(
        's3',
        endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
        region_name=os.getenv("ru-central1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )


def get_unique_hash():
    for attempts in range(100):
        random_bytes = os.urandom(10)
        coded_bytes = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        coded_bytes.replace('=', '')
        _hash = coded_bytes[:7]

        if not Paste.objects.filter(hash=_hash).exists():
            return _hash

    raise ValueError("Не удалось найти уникальный хэш. Повторите позже")
