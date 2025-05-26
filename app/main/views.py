from .models import Cart, CartItem, Product, CustomUser, PaymentCard, Material
from .forms import RegistrationForm, ProductForm, PaymentCardForm, AddressForm, ReviewForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.views import View
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt 
from django.utils.decorators import method_decorator
from main.models import Article, Order, OrderItem, CustomUser, Review, Contacts
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required

def home(request):
    latest_reviews = Review.objects.filter(is_published=True).order_by('-created_at')[:3]
    latest_products = Product.objects.order_by('-created_at')[:6]
    latest_articles = Article.objects.filter(status='published').order_by('-created_at')[:3]
    
    context = {
        'latest_products': latest_products,
        'latest_articles': latest_articles,
        'latest_reviews': latest_reviews,
    }
    return render(request, 'home.html', context)

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
        email = request.POST.get('username')  
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
            
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                login(request, auth_user)
                return redirect('profile')
        except CustomUser.DoesNotExist:
            pass  

        return render(request, 'login.html', {'error': 'Неверный email или пароль'})
        
class ProfileView(LoginRequiredMixin, View):
    
    def get(self, request):
        context = {
            'card_form': PaymentCardForm(),
            'address_form': AddressForm(),
            'cards': self._get_formatted_cards(request),
            'addresses': request.user.address or [],
            'orders': Order.objects.filter(user=request.user).order_by('-id')
        }
        return render(request, 'profile.html', context)

    def post(self, request):
        form_type = 'card' if 'add_card' in request.POST else 'address'
        form = PaymentCardForm(request.POST) if form_type == 'card' else AddressForm(request.POST)
        
        if form.is_valid():
            if form_type == 'card':
                card = form.save(commit=False)
                card.user = request.user
                card.save()
            else:
                addresses = request.user.address or []
                addresses.append(form.cleaned_data)
                request.user.address = addresses
                request.user.save()
            return redirect('profile')
        
        # Если форма невалидна
        context = self.get(request).context_data
        if form_type == 'card':
            context['card_form'] = form
        else:
            context['address_form'] = form
        return render(request, 'profile.html', context)

    def _get_formatted_cards(self, request):
        cards = request.user.payment_cards.all()
        for card in cards:
            digits = ''.join(filter(str.isdigit, card.card_number))
            card.formatted_number = ' '.join([digits[i:i+4] for i in range(0, len(digits), 4)])
        return cards


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        if not order_id:
            return JsonResponse({'error': 'Order ID required'}, status=400)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            items = order.orderitem_set.select_related('product').values(
                'product__name',
                'product__image',
                'product__price',
                'quantity'
            )
            
            return JsonResponse({
                'order_id': order.id,
                'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
                'products': list(items)
            })
            
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Server error'}, status=500)
        
    
def logout_view(request):
    logout(request)
    return redirect("home")

def about(request):
    return render(request, 'about.html')

def catalog(request):
    products = Product.objects.all()

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

@staff_member_required
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

@login_required
def order(request):
    cart = request.user.cart
    if request.method == 'POST':
        # Получаем выбранные карту и адрес
        card = request.user.payment_cards.filter(id=request.POST.get('payment_card')).first()
        try:
            address_index = int(request.POST.get('delivery_address'))
            address = request.user.address[address_index] if 0 <= address_index < len(request.user.address or []) else None
        except (ValueError, TypeError):
            address = None

        if not card or not address:
            return render_order_page(request, cart, error="Пожалуйста, выберите корректную карту и адрес доставки")

        # Создаем заказ
        order = create_order(request.user, cart, card, address)
        cart.items.all().delete()  # Очищаем корзину
        return redirect('profile')

    return render_order_page(request, cart)

# Вспомогательные функции
def render_order_page(request, cart, error=None):
    items = [{
        'product': item.product,
        'quantity': item.quantity,
        'item_total_price': item.product.price * item.quantity
    } for item in cart.items.select_related('product')]

    cards = request.user.payment_cards.all()
    for card in cards:
        digits = ''.join(filter(str.isdigit, card.card_number))
        card.formatted_number = ' '.join([digits[i:i+4] for i in range(0, len(digits), 4)])

    return render(request, 'order.html', {
        'cart': {'items': items, 'total_price': sum(i['item_total_price'] for i in items)},
        'cards': cards,
        'addresses': request.user.address or [],
        'error_message': error
    })

def create_order(user, cart, card, address):
    order = Order.objects.create(
        user=user,
        payment_card=card,
        delivery_address=address if isinstance(address, dict) else address.__dict__,
        total_price=0
    )
    
    total = 0
    for item in cart.items.select_related('product'):
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )
        total += item.product.price * item.quantity
    
    order.total_price = total
    order.save()
    return order

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
    adress = Contacts.objects.all()
    
    context = {
        'adress' : adress,
    }
    return render(request, 'contacts.html', context)


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

def all_reviews(request):
    # Все опубликованные отзывы
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'all_reviews.html', {'reviews': reviews})

@login_required
def manage_review(request):
    # Получаем отзыв пользователя (если есть)
    user_review = Review.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=user_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('home')
    else:
        form = ReviewForm(instance=user_review)
    
    return render(request, 'manage_review.html', {
        'form': form,
        'user_review': user_review
    })