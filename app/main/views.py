from django.shortcuts import render, redirect
from .models import Product, CustomUser
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, AddCardForm, ProductForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

def home(request):
    return render(request, "home.html")

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
        return render(request, 'register.html', {'form': form})

class CustomLoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Нормализация номера
        if any(c.isdigit() for c in username):
            digits = ''.join(filter(str.isdigit, username))
            if digits.startswith('8'):
                digits = '7' + digits[1:]
            if digits.startswith('9'):
                digits = '7' + digits
            username = f'+7{digits[1:11]}'

        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('profile')
            
        return render(request, 'login.html', {'error': 'Неверные данные'})



class ProfileView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        form = AddCardForm()
        return render(request, 'profile.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect("home")

def about(request):
    return render(request, 'about.html')

def catalog(request):
    products = Product.objects.all()
    return render(request, 'catalog.html')

def order(request):
    if request.method == 'POST':
        pass
    return render(request, 'order.html')

def contacts(request):
    return render(request, 'contacts.html')
