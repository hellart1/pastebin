from django import forms
from django.contrib.auth.forms import UserCreationForm


class TextForm(forms.Form):
    paste_text = forms.CharField()
    expiration = forms.CharField()


