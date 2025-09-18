import base64

import boto3
from django.shortcuts import render, get_object_or_404, redirect

from .forms import TextForm
from .models import Paste
from django.conf import settings
import os
from datetime import datetime, timedelta


class ObjectMixin:
    model = None
    template_name = None

    def get(self, request, *args, **kwargs):
        data = args
        if not data:
            return render(request, self.template_name)
        paste = get_object_or_404(self.model, hash=data)
        obj = s3_resource().get_object(
            Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
            Key=paste.s3_key
        )["Body"].read().decode('utf-8')

        return render(request, self.template_name, context={'content': obj})

    def post(self, request):
        form = TextForm(request.POST or None)
        # Проверка валидности формы
        if form.is_valid():
            # Передача текста в переменную из textarea
            paste_text = form.cleaned_data['paste_text']
            dhash = get_unique_hash()

        self.model.objects.create(
            s3_key=paste_text
        )

        now = datetime.now()
        expire = now + timedelta(minutes=1)

        s3_resource().Bucket(
            os.getenv("AWS_STORAGE_BUCKET_NAME")
        ).put_object(
            Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
            Key=f"{dhash}.txt",
            Body=dhash,
            Expires=expire
            )

        return redirect("user_text", data=dhash)


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


def upload_to_s3(self, key, content):
    return get_s3_resource().put_object(Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"), Key=key, Body=content)


def download_from_s3(self, key):
    obj = get_s3_resource().get_object(Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"), Key=key)
    return obj['Body'].read().decode('utf-8')


def get_unique_hash():
    for attempts in range(100):
        random_bytes = os.urandom(10)
        coded_bytes = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        coded_bytes.replace('=', '')
        _hash = coded_bytes[:7]

        if not Paste.objects.filter(s3_key=_hash).exists():
            return _hash

    raise ValueError("Не удалось найти уникальный хэш. Повторите позже")


class S3_params:

    def __init__(self):
        self.endpoint_url = settings.AWS_S3_ENDPOINT_URL,
        self.region_name = settings.AWS_S3_REGION_NAME,
        self.aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
        self.aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
        self.storage_bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def get_s3_resource(self):
        return boto3.resource(
            's3',
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def upload_to_s3(self, key, content):
        return self.get_s3_resource().put_object(Bucket=self.storage_bucket_name, Key=key, Body=content)

    def download_from_s3(self, key):
        obj = self.get_s3_resource().get_object(Bucket=self.storage_bucket_name, Key=key)
        return obj['Body'].read().decode('utf-8')
