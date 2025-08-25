from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from botocore.exceptions import BotoCoreError, ClientError
from django.db import IntegrityError, DatabaseError

from .forms import TextForm
from .models import Paste
from .s3_utils import get_s3_resource, get_unique_hash


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

                s3_resource = get_s3_resource()
                bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
                bucket.put_object(
                    Key=f"{data_hash}.txt",
                    Body=paste_text,
                )

                # Создание записи в бд
                Paste.objects.create(
                    hash=data_hash,
                    s3_key=f"{data_hash}.txt"
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
        s3_resource = get_s3_resource()
        bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
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
