from django import forms


class TextForm(forms.Form):
    paste_text = forms.CharField()
