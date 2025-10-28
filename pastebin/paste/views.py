import datetime
import os
import requests
from datetime import timedelta, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
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
from .utils import *


class Home(S3UtilsMixin, FormView):
    form_class = TextForm
    template_name = "paste/home.html"
    model = Paste
    context_object_name = "content"

    def get_success_url(self):
        return reverse_lazy('user_text', kwargs={'data': self.paste_hash})

    def form_valid(self, form):
        print('form_valid')
        paste_text = form.cleaned_data['paste_text']
        self.paste_hash = get_unique_hash()
        # max_size = 10 * 1024 * 10244
        lifespan = form.cleaned_data['expiration']
        # lifespan = 10
        print(self.paste_hash, lifespan)

        self.put_object_in_s3(
            file_hash=self.paste_hash,
            text=paste_text
        )
        print('put_object_in_s3')

        self.model.objects.create(hash=self.paste_hash, expiration_type=lifespan)
        print('создался обьект в бд')
        return super().form_valid(form)


class User_text(DetailView):
    model = Paste
    template_name = "paste/user_text.html"
    context_object_name = 'post'

    def get_object(self, queryset=None):
        endpoint = reverse('paste_api', kwargs={'hash': self.kwargs.get('data')})
        print(endpoint)
        try:
            response = requests.get(
                self.request.build_absolute_uri(endpoint)
            ).json()
            print(response)

            content = requests.get(response['download_url'])
            if content.status_code == 200:
                return content.text

        except Exception as e:
            print(f'Ошибка: {e}')
            raise Http404


class EditPaste(LoginRequiredMixin, S3UtilsMixin, FormView):
    login_url = reverse_lazy('users:login')
    form_class = TextForm
    template_name = 'paste/edit_paste.html'
    context_object_name = 'data'

    def get_success_url(self):
        return reverse_lazy('user_text', kwargs={'data': self.kwargs.get('data')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hash'] = self.kwargs.get('data')

        return context

    def form_valid(self, form):

        self.put_object_in_s3(
            file_hash=self.kwargs.get('data'),
            text=form.cleaned_data['paste_text']
        )

        return super().form_valid(form)


class PasteAPIList(PasteExpirationMixin, generics.RetrieveAPIView):
    queryset = Paste.objects.all()
    serializer_class = PasteSerializer
    lookup_field = 'hash'

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        presigned_url = self.expiration_handler(obj)
        serializer = self.get_serializer_class()(obj, context={'download_url': presigned_url})

        return Response(serializer.data)


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
