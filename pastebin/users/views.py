from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm, LoginForm


# def signup(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('users:login')
#     else:
#         form = RegisterForm()
#
#     return render(request, 'users/signup.html', {'form': form})


class RegisterUser(CreateView):
    form_class = RegisterForm
    template_name = 'users/signup.html'

    def get_success_url(self):
        return reverse_lazy('home')

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            return redirect('users:login')
    else:
        form = RegisterForm()

    return render(request, 'users/signup.html', {'form': form})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = "users/login.html"
