from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm, LoginForm


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = "users/login.html"


class RegisterUser(CreateView):
    form_class = RegisterForm
    template_name = 'users/signup.html'

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))
