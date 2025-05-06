from django.shortcuts import render
from .models import Product
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, LoginForm

def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

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
