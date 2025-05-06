from django import forms
from .models import Order
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=150, label='Имя')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=20, label='Телефон')

    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'password1', 'password2')

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'placeholder': 'Ваши пожелания и комментарии...',
                'rows': 4
            }),
        }