from django.urls import path, include
from . import views
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('<str:data>', User_text.as_view(), name='user_text'),
    # path('api/paste/', PasteAPIList.as_view(), name='paste_api'),
    path('api/paste/<str:hash>/', PasteAPIList.as_view(), name='paste_api')
]