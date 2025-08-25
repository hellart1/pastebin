from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user_text/<str:data>', views.user_text, name='user_text'),
]