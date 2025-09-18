from django.urls import path, include
from . import views
from .views import Home, User_text

urlpatterns = [
    # path('', views.home, name='home'),
    path('', Home.as_view(), name='home'),
    # path('user_text/<str:data>', User_text.as_view(), name='user_text'),
    path('user_text/<str:data>', User_text.as_view(), name='user_text'),
]