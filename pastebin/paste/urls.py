from django.urls import path, include
from . import views
from .views import Home, User_text, ModelAPIView

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('user_text/<str:data>', User_text.as_view(), name='user_text'),
    path('api/paste/', ModelAPIView.as_view(), name='paste_api')
]