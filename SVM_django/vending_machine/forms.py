from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Bottle


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class BottleForm(forms.ModelForm):
    class Meta:
        model = Bottle
        fields = ['name', 'description', 'price', 'stock', 'image_url']
