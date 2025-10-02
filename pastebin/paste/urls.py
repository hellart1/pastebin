from django.urls import path, include
from . import views
from .views import Home, User_text, ErrorView

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('user_text/<str:data>', User_text.as_view(), name='user_text'),
]