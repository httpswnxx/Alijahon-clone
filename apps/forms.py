import re

from django.contrib.auth.forms import PasswordChangeForm
from django.forms.fields import CharField
from django.forms import Form, ModelForm
from django.forms.widgets import PasswordInput

from apps.models import User
from django import forms


class AuthForm(Form):
    phone_number = CharField(max_length=20)
    password = CharField(max_length=20)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        digits_only = re.sub(r"\D", "", phone_number)
        return "+" + digits_only

    def save(self):
        phone_number = self.cleaned_data.get("phone_number")
        password = self.cleaned_data.get("password")

        user = User.objects.create(phone_number=phone_number, password=password)
        return user

class ProfileUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'profile_image']

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
