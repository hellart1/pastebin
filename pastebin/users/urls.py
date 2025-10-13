from django.contrib.auth.views import LogoutView
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    path('signup', views.RegisterUser.as_view(), name='signup'),
    path('login', views.LoginUser.as_view(), name='login'),
    path('logout', views.logout_user, name='logout')
]