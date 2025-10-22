from django.http import HttpResponseNotFound
from django.urls import path, include
from . import views
from .views import *


def favicon_not_found(request):
    return HttpResponseNotFound()


urlpatterns = [
    path('favicon.ico', favicon_not_found),
    path('<str:data>', User_text.as_view(), name='user_text'),
    path('api/paste/<str:hash>/', PasteAPIList.as_view(), name='paste_api'),
    path('', Home.as_view(), name='home'),
]