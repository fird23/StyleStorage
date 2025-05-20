from .models import Cart, CartItem, Product, CustomUser, PaymentCard, Material
from .forms import RegistrationForm, AddCardForm, ProductForm, PaymentCardForm, UserProfileForm, AddressForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.views import View
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from main.models import Article, Order, OrderItem
from collections import Counter

def home(request):
    latest_products = Product.objects.order_by('-created_at')[:6]
    latest_articles = Article.objects.filter(status='published').order_by('-created_at')[:3]
    
    context = {
        'latest_products': latest_products,
        'latest_articles': latest_articles,
    }
    return render(request, "home.html", context)

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

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

        # Получаем историю заказов пользователя
        orders = Order.objects.filter(user=request.user).order_by('-id')

        return render(request, 'profile.html', {'card_form': card_form, 'cards': cards, 'addresses': addresses, 'orders': orders})

    def post(self, request):
        if 'add_card' in request.POST:
            card_form = PaymentCardForm(request.POST)
            if card_form.is_valid():
                new_card = card_form.save(commit=False)
                new_card.user = request.user
                new_card.save()
                return redirect('profile')
            else:
                cards = request.user.payment_cards.all()
                for card in cards:
                    digits_only = ''.join(filter(str.isdigit, card.card_number))
                    card.formatted_number = ' '.join([digits_only[i:i+4] for i in range(0, len(digits_only), 4)])
                addresses = request.user.address if request.user.address else []
                orders = Order.objects.filter(user=request.user).order_by('-id')
                return render(request, 'profile.html', {'card_form': card_form, 'cards': cards, 'addresses': addresses, 'orders': orders})
        elif 'add_address' in request.POST:
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                user = request.user
                addresses = user.address if user.address else []
                if not isinstance(addresses, list):
                    addresses = []
                addresses.append(address_form.cleaned_data)
                user.address = addresses
                user.save()
                return redirect('profile')
            else:
                card_form = PaymentCardForm()
                cards = request.user.payment_cards.all()
                for card in cards:
                    digits_only = ''.join(filter(str.isdigit, card.card_number))
                    card.formatted_number = ' '.join([digits_only[i:i+4] for i in range(0, len(digits_only), 4)])
                addresses = user.address if user.address else []
                orders = Order.objects.filter(user=request.user).order_by('-id')
                return render(request, 'profile.html', {'card_form': card_form, 'addresses': addresses, 'cards': cards, 'address_form': address_form, 'orders': orders})
        # Handle other POST actions if any
        return redirect('profile')

@method_decorator(csrf_exempt, name='dispatch')
class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)
        order_id = request.GET.get('order_id')
        if not order_id:
            logger.error('Order ID not provided in request')
            return JsonResponse({'error': 'Order ID not provided'}, status=400)
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            logger.error(f'Order not found: id={order_id} for user={request.user}')
            return JsonResponse({'error': 'Order not found'}, status=404)
        try:
            # Предполагается, что у заказа есть связанная модель OrderItem с количеством и продуктом
            order_items = order.orderitem_set.select_related('product').all()
            product_list = []
            for item in order_items:
                product_list.append({
                    'name': item.product.name,
                    'image_url': item.product.image.url if item.product.image else '',
                    'price': str(item.product.price),
                    'quantity': item.quantity,
                })
            data = {
                'order_id': order.id,
                'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
                'products': product_list,
            }
            return JsonResponse(data)
        except Exception as e:
            logger.exception(f'Error while processing order details for order id={order_id}')
            # Временно возвращаем текст ошибки для отладки
            return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)

def logout_view(request):
    logout(request)
    return redirect("home")

def about(request):
    return render(request, 'about.html')

def catalog(request):
    products = Product.objects.all()

    # Получение параметров фильтрации из GET-запроса
    search_query = request.GET.get('search', '')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    categories = request.GET.getlist('category')
    materials = request.GET.getlist('material')

    if search_query:
        products = products.filter(name__icontains=search_query)
    if price_min:
        try:
            price_min_val = float(price_min)
            products = products.filter(price__gte=price_min_val)
        except ValueError:
            pass
    if price_max:
        try:
            price_max_val = float(price_max)
            products = products.filter(price__lte=price_max_val)
        except ValueError:
            pass
    if categories:
        products = products.filter(category__in=categories)
    if materials:
        products = products.filter(material__in=materials)

    # Получаем все материалы для фильтрации
    all_materials = Material.objects.all()

    # Пагинация - 6 товаров на страницу
    paginator = Paginator(products, 6)
    page = request.GET.get('page')

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    context = {
        'products': products_page,
        'search_query': search_query,
        'price_min': price_min,
        'price_max': price_max,
        'selected_categories': categories,
        'selected_materials': materials,
        'all_materials': all_materials,
        'page_obj': products_page,
        'paginator': paginator,
    }
    return render(request, 'catalog.html', context)

@user_passes_test(lambda u: u.is_staff)
def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return redirect('catalog')
    else:
        return HttpResponseForbidden("Метод не разрешен")

class CartContext:
    def __init__(self, items, total_price):
        self.items = items
        self.total_price = total_price

@require_POST
def add_to_cart(request, product_id):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()
    return JsonResponse({'success': True, 'cart_count': sum(item.quantity for item in cart.items.all())})

def order(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    cart, created = Cart.objects.get_or_create(user=user)
    if request.method == 'POST':
        card_id = request.POST.get('payment_card')
        address_index = request.POST.get('delivery_address')
        cards = user.payment_cards.all()
        addresses = user.address if user.address else []
        # Validate card
        try:
            selected_card = cards.get(id=card_id)
        except (PaymentCard.DoesNotExist, ValueError, TypeError):
            selected_card = None
        # Validate address
        try:
            address_index = int(address_index)
            if 0 <= address_index < len(addresses):
                selected_address = addresses[address_index]
            else:
                selected_address = None
        except (ValueError, TypeError):
            selected_address = None
        if not selected_card or not selected_address:
            items = []
            total_price = 0
            for item in cart.items.select_related('product').all():
                item_total_price = float(item.product.price) * item.quantity
                items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'item_total_price': item_total_price,
                })
                total_price += item_total_price
            cart_obj = CartContext(items, total_price)
            error_message = "Пожалуйста, выберите корректную карту и адрес доставки."
            return render(request, 'order.html', {'cart': cart_obj, 'cards': cards, 'addresses': addresses, 'error_message': error_message})
        # Calculate total price
        total_price = 0
        # Create order
        # delivery_address должен быть словарем, а не объектом
        delivery_address_data = None
        if selected_address:
            if isinstance(selected_address, dict):
                delivery_address_data = selected_address
            else:
                # Преобразуем объект адреса в словарь, если нужно
                delivery_address_data = {
                    'city': getattr(selected_address, 'city', ''),
                    'street': getattr(selected_address, 'street', ''),
                    'house': getattr(selected_address, 'house', ''),
                    'apartment': getattr(selected_address, 'apartment', ''),
                }
        order = Order.objects.create(
            user=user,
            total_price=0,
            payment_card=selected_card,
            delivery_address=delivery_address_data
        )
        total_price = 0
        for item in cart.items.select_related('product').all():
            total_price += item.product.price * item.quantity
            # Создаем OrderItem для каждого товара
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
        order.total_price = total_price
        order.save()
        # Clear cart
        cart.items.all().delete()
        return redirect('profile')
    else:
        items = []
        total_price = 0
        for item in cart.items.select_related('product').all():
            item_total_price = item.product.price * item.quantity
            items.append({
                'product': item.product,
                'quantity': item.quantity,
                'item_total_price': item_total_price,
            })
            total_price += item_total_price
        cart_obj = CartContext(items, total_price)
        cards = user.payment_cards.all()
        for card in cards:
            digits_only = ''.join(filter(str.isdigit, card.card_number))
            card.formatted_number = ' '.join([digits_only[i:i+4] for i in range(0, len(digits_only), 4)])
        addresses = user.address if user.address else []
        return render(request, 'order.html', {'cart': cart_obj, 'cards': cards, 'addresses': addresses})

@require_POST
@login_required
def remove_from_cart(request, product_id):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        return JsonResponse({'success': False, 'error': 'Корзина не найдена'})

    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден в корзине'})

@require_http_methods(["POST"])
def update_cart_item_quantity(request, product_id):
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"update_cart_item_quantity called with product_id={product_id} and POST data={request.POST}")
    user = request.user
    if not user.is_authenticated:
        logger.warning("User not authenticated")
        return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        logger.warning("Cart not found")
        return JsonResponse({'success': False, 'error': 'Cart not found'}, status=404)
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.quantity = quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        logger.warning("Cart item not found")
        return JsonResponse({'success': False, 'error': 'Cart item not found'}, status=404)
    # Пересчёт общей суммы корзины
    total_price = 0
    for item in cart.items.select_related('product').all():
        total_price += item.product.price * item.quantity
    logger.info(f"Quantity updated successfully: {cart_item.quantity}, total_price={total_price}")
    return JsonResponse({
        'success': True,
        'quantity': cart_item.quantity,
        'item_total_price': float(cart_item.product.price) * cart_item.quantity,
        'total_price': float(total_price)
    })

def product_modal(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404("Товар не найден")
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'material': product.material.name if product.material else '',
        'category_display': product.get_category_display(),
        'dimensions': product.dimensions if product.dimensions else '',
        'image_url': product.image.url if product.image else '',
    }
    return JsonResponse(product_data)

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

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, status='published')
    return render(request, 'article_detail.html', {'article': article})