from .models import Product, CustomUser, PaymentCard
from .forms import RegistrationForm, AddCardForm, ProductForm, PaymentCardForm, UserProfileForm, AddressForm
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.views import View
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
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
        input_username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = None

        # Попытка найти пользователя по email
        try:
            user_obj = CustomUser.objects.get(email=input_username)
        except CustomUser.DoesNotExist:
            user_obj = None

        # Если не найден по email, пытаемся по телефону
        if not user_obj:
            if any(c.isdigit() for c in input_username):
                digits = ''.join(filter(str.isdigit, input_username))
                if digits.startswith('8'):
                    digits = '7' + digits[1:]
                if digits.startswith('9'):
                    digits = '7' + digits
                phone_normalized = f'+7{digits[1:11]}'
                try:
                    user_obj = CustomUser.objects.get(phone=phone_normalized)
                except CustomUser.DoesNotExist:
                    user_obj = None

        # Если пользователь найден, используем его username для аутентификации
        if user_obj:
            user = authenticate(username=user_obj.username, password=password)
            if user:
                login(request, user)
                return redirect('profile')

        # Если не найден или пароль неверный
        return render(request, 'login.html', {'error': 'Неверные данные'})

class ProfileView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        card_form = PaymentCardForm()
        cards = request.user.payment_cards.all()
        # Добавим форматирование номера карты для отображения
        for card in cards:
            digits_only = ''.join(filter(str.isdigit, card.card_number))
            card.formatted_number = ' '.join([digits_only[i:i+4] for i in range(0, len(digits_only), 4)])
        addresses = request.user.address if request.user.address else []
        return render(request, 'profile.html', {'card_form': card_form, 'cards': cards, 'addresses': addresses})

    def post(self, request):
        if 'save_profile' in request.POST:
            user_form = UserProfileForm(request.POST, instance=request.user)
            card_form = PaymentCardForm()
            if user_form.is_valid():
                user = user_form.save()
                # Re-authenticate user to update session with new credentials
                update_session_auth_hash(request, user)
                return redirect('profile')
            cards = request.user.payment_cards.all()
            for card in cards:
                card.formatted_number = ' '.join([card.card_number[i:i+4] for i in range(0, len(card.card_number), 4)])
            return render(request, 'profile.html', {'user_form': user_form, 'card_form': card_form, 'cards': cards})
        elif 'add_card' in request.POST:
            card_form = PaymentCardForm(request.POST)
            user_form = UserProfileForm(instance=request.user)
            if card_form.is_valid():
                payment_card = card_form.save(commit=False)
                payment_card.user = request.user
                payment_card.save()
                return redirect('profile')
            cards = request.user.payment_cards.all()
            for card in cards:
                card.formatted_number = ' '.join([card.card_number[i:i+4] for i in range(0, len(card.card_number), 4)])
            return render(request, 'profile.html', {'user_form': user_form, 'card_form': card_form, 'cards': cards})
        elif 'add_address' in request.POST:
            address_form = AddressForm(request.POST)
            user_form = UserProfileForm(instance=request.user)
            card_form = PaymentCardForm()
            if address_form.is_valid():
                address_data = address_form.cleaned_data
                user = request.user
                # Получаем текущие адреса из JSONField
                addresses = user.address if user.address else []
                if not isinstance(addresses, list):
                    addresses = []
                addresses.append({
                    'city': address_data['city'],
                    'street': address_data['street'],
                    'house': address_data['house'],
                    'apartment': address_data.get('apartment', '')
                })
                user.address = addresses
                user.save()
                return redirect('profile')
            cards = request.user.payment_cards.all()
            for card in cards:
                card.formatted_number = ' '.join([card.card_number[i:i+4] for i in range(0, len(card.card_number), 4)])
            return render(request, 'profile.html', {'user_form': user_form, 'card_form': card_form, 'address_form': address_form, 'cards': cards})
        else:
            user_form = UserProfileForm(instance=request.user)
            card_form = PaymentCardForm()
            address_form = AddressForm()
            cards = request.user.payment_cards.all()
            for card in cards:
                card.formatted_number = ' '.join([card.card_number[i:i+4] for i in range(0, len(card.card_number), 4)])
            return render(request, 'profile.html', {'user_form': user_form, 'card_form': card_form, 'address_form': address_form, 'cards': cards})

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


def delete_card(request, card_id):
    if request.method == 'POST':
        try:
            card = PaymentCard.objects.get(id=card_id, user=request.user)
            card.delete()
            return redirect('profile')
        except PaymentCard.DoesNotExist:
            return HttpResponseForbidden("Нет доступа к удалению этой карты")
    else:
        return HttpResponseForbidden("Метод не разрешен")

def delete_address(request, index):
    if request.method == 'POST':
        user = request.user
        addresses = user.address if user.address else []
        if not isinstance(addresses, list):
            addresses = []
        try:
            index = int(index)
            if 0 <= index < len(addresses):
                addresses.pop(index)
                user.address = addresses
                user.save()
                return redirect('profile')
            else:
                return HttpResponseForbidden("Неверный индекс адреса")
        except (ValueError, TypeError):
            return HttpResponseForbidden("Неверный индекс адреса")
    else:
        return HttpResponseForbidden("Метод не разрешен")
