import os
import requests
from django.forms import model_to_dict

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from botocore.exceptions import BotoCoreError, ClientError
from django.db import IntegrityError, DatabaseError
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, View, DetailView, TemplateView
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import TextForm
from .models import Paste
from .s3_utils import get_unique_hash, s3_resource, s3_client
from .serializers import PasteSerializer
from .utils import StrObjectMixin


class Home(FormView):
    form_class = TextForm
    template_name = "paste/home.html"
    model = Paste
    context_object_name = "content"

    def get_success_url(self):
        return reverse_lazy('user_text', kwargs={'data': self.paste_hash})

    def create_presigned_url(self, client, bucket_name, object_name, expiration):

        try:
            return client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )

        except ClientError as e:
        # logging.error(e)
            return None

    def put_object_in_s3(self, resource, bucket_name, file_hash, text):
        bucket = resource.Bucket(bucket_name)
        return bucket.put_object(
            Key=f"{file_hash}.txt",
            Body=text
        )


    def form_valid(self, form):
        paste_text = form.cleaned_data['paste_text']
        self.paste_hash = get_unique_hash()
        # max_size = 10 * 1024 * 10244
        lifespan = form.cleaned_data['expiration']
        # lifespan = 10

        self.put_object_in_s3(
            resource=s3_resource(),
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            file_hash=self.paste_hash,
            text=paste_text
        )

        presigned_url = self.create_presigned_url(
            client=s3_client(),
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            object_name=f"{self.paste_hash}.txt",
            expiration=lifespan
        )

        self.model.objects.create(hash=self.paste_hash, url=presigned_url)

        return super().form_valid(form)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['post'] = self.download_from_s3(key=)


class User_text(DetailView):
    model = Paste
    template_name = "paste/user_text.html"
    context_object_name = 'post'

    def get_object_from_s3(self, resource, bucket_name, s3_key):
        bucket = resource.Bucket(bucket_name)
        obj = bucket.Object(f"{s3_key}.txt")
        return obj.get()['Body'].read().decode('utf-8')

    def get_object(self, queryset=None):
        data_param = self.kwargs.get("data")
        user_object = self.model.objects.get(hash=data_param)

        if user_object:
            content = requests.get(user_object.url)
            if content.status_code == 200:
                return content.text
            else:
                raise Http404


class ErrorView(TemplateView):
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = self.get_error_message(context['status_code'])

        return context

    def get_error_message(self, status_code):
        messages = {
            404: 'Page not found',
            500: 'Server error',
            403: 'Forbidden',
        }

        return messages.get(status_code, 'Something went wrong')

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = context['status_code']

        return super().render_to_response(context, **response_kwargs)


class ModelAPIView(APIView):
    def get(self, request):
        lst = Paste.objects.all().values()
        return Response({'post': list(lst)})

    def post(self, request):
        post_new = Paste.objects.create(
            hash=request.data['hash']
        )
        return Response({'post': model_to_dict(post_new)})
