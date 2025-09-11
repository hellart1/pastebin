import os

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from botocore.exceptions import BotoCoreError, ClientError
from django.db import IntegrityError, DatabaseError
from django.urls import reverse_lazy
from django.views.generic import FormView, View

from .forms import TextForm
from .models import Paste
from .s3_utils import ObjectMixin, get_unique_hash, s3_resource


class Home(FormView):
    form_class = TextForm
    template_name = "paste/home.html"
    success_url = reverse_lazy('home')
    context_object_name = "content"
    model = Paste

    def put_object_in_s3(self, resource, bucket_name, file_hash, text):
        bucket = resource.Bucket(bucket_name)
        return bucket.put_object(
            Key=f"{file_hash}.txt",
            Body=text
        )

    def create_object_in_model(self, model: object, field, obj):
        return model.objects.create(
            **{field: obj}
        )

    def form_valid(self, form):
        paste_text = form.cleaned_data['paste_text']
        paste_hash = get_unique_hash()

        self.put_object_in_s3(
            resource=s3_resource(),
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            file_hash=paste_hash,
            text=paste_text
        )
        # resource = s3_resource()
        # bucket = resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        # bucket.put_object(
        #     Key=f"{paste_hash}.txt",
        #     Body=paste_text
        # )

        self.create_object_in_model(
            model=self.model,
            field="s3_key",
            obj=paste_hash
        )

        return super().form_valid(form)


class User_text(View):
    model = Paste
    template_name = "paste/user_text.html"

def home(request):
    if request.method == 'POST':
        # Создание текста формы из запроса
        form = TextForm(request.POST or None)
        # Проверка валидности формы
        if form.is_valid():
            try:
                # Передача текста в переменную из textarea
                paste_text = form.cleaned_data['paste_text']
                data_hash = get_unique_hash()

                resource = s3_resource()
                bucket = resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
                bucket.put_object(
                    Key=f"{data_hash}.txt",
                    Body=paste_text,
                )


                # Создание записи в бд
                Paste.objects.create(
                    s3_key=data_hash
                )

                return redirect('user_text', data=data_hash)
            except (BotoCoreError, ClientError) as e:
                # Ошибка загрузки в AWS
                # logger
                form.add_error(None, "Loading error. Try later")
            except (IntegrityError, DatabaseError) as e:
                # logger
                form.add_error(None, 'Database error. Try later')
            except (ValueError) as e:
                # Ошибка конфигурации AWS или генерации хэша
                # logger
                form.add_error(None, 'Service configuration error. Try later')
            except Exception as e:
                form.add_error(None, 'Unexpected error. Try later')
    else:
        # Создание пустой формы если например 'GET' запрос
        form = TextForm()

    return render(request, 'paste/home.html', {'form': form})


def user_text(request, data):
    try:
        paste = get_object_or_404(Paste, hash=data)
        resource = s3_resource()
        bucket = resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        obj = bucket.Object(paste.s3_key)
        content = obj.get()['Body'].read().decode('utf-8')

        context = {
            'content': content,
        }

        return render(request, 'paste/user_text.html', context=context)
    except (BotoCoreError, ClientError) as e:
        # logger
        return render(request, 'paste/error.html',
                      context={'error': 'Не удалось загрузить содержимое'})
