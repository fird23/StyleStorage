from django import forms
from .models import CustomUser, Product, Order, PaymentCard, Review
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'material', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Описание изделия...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'style': 'padding: 0.8rem; border-radius: 5px;'
            }),
            'material': forms.Select(attrs={
                'class': 'form-control',
                'style': 'padding: 0.8rem; border-radius: 5px;'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AddCardForm(forms.Form):
    card_number = forms.CharField(max_length=19)
    expiry_date = forms.CharField(max_length=7)
    cvv = forms.CharField(max_length=3)

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

class PaymentCardForm(forms.ModelForm):
    class Meta:
        model = PaymentCard
        fields = ['card_number', 'expiry_date']
        widgets = {
            'card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер карты',
                'maxlength': 19,
            }),
            'expiry_date': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ММ/ГГ',
                'maxlength': 5,
            }),
        }

class UserProfileForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class AddressForm(forms.Form):
    city = forms.CharField(max_length=100, required=True, label='Город')
    street = forms.CharField(max_length=100, required=True, label='Улица')
    house = forms.CharField(max_length=20, required=True, label='Дом')
    apartment = forms.CharField(max_length=20, required=False, label='Квартира')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв здесь...'
            }),
        }