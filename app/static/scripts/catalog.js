document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('productModal');

    function openProductModal(productId) {
        fetch(`/product/${productId}/modal/`)
            .then(response => response.json())
            .then(product => {
                document.getElementById('modal-product-name').textContent = product.name;
                document.getElementById('modal-product-image').src = product.image_url;
                document.getElementById('modal-product-image').alt = product.name;
                document.getElementById('modal-product-description').textContent = product.description;
                document.getElementById('modal-product-material').textContent = product.material;
                document.getElementById('modal-product-category').textContent = product.category_display;
                document.getElementById('modal-product-dimensions').textContent = product.dimensions;
                document.getElementById('modal-product-price').textContent = product.price;
                modal.style.display = 'flex';
            })
            .catch(error => {
                console.error('Ошибка загрузки данных товара:', error);
            });
    }

    function closeProductModal() {
        modal.style.display = 'none';
    }

    document.querySelectorAll('.details-btn').forEach(btn => {
        btn.addEventListener('click', event => {
            event.preventDefault();
            const productId = btn.dataset.productId;
            openProductModal(productId);
        });
    });

    if (modal) {
        const closeBtn = modal.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeProductModal);
        }
    }

    // Обработчик клика для кнопок "Добавить в корзину"
    document.querySelectorAll('.btn-cart').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.getAttribute('data-product-id');
            if (productId) {
                addToCart(productId);
            }
        });
    });

    // Делегирование событий для кнопок изменения количества товара
    const cartItemsContainer = document.querySelector('.cart-items');
    if (cartItemsContainer) {
        cartItemsContainer.addEventListener('click', (event) => {
            const button = event.target.closest('.quantity-btn');
            if (!button) return;

            const cartItemDiv = button.closest('.cart-item');
            if (!cartItemDiv) return;

            const productId = cartItemDiv.getAttribute('data-product-id');
            const quantitySpan = cartItemDiv.querySelector('.quantity');
            const priceDiv = cartItemDiv.querySelector('.price');
            if (!productId || !quantitySpan || !priceDiv) return;

            let currentQuantity = parseInt(quantitySpan.textContent);
            if (isNaN(currentQuantity)) currentQuantity = 1;

            if (button.classList.contains('plus')) {
                currentQuantity += 1;
            } else if (button.classList.contains('minus')) {
                if (currentQuantity > 1) {
                    currentQuantity -= 1;
                } else {
                    return; // Не уменьшаем меньше 1
                }
            }

            // Отправляем запрос на обновление количества
            updateCartItemQuantity(productId, currentQuantity, quantitySpan, priceDiv);
        });
    }

    window.openProductModal = openProductModal;
    window.closeProductModal = closeProductModal;
});

function addToCart(productId) {
    console.log('addToCart called with productId:', productId);
    console.log('Sending POST request to add_to_cart');
    fetch(`/add_to_cart/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => {
        console.log('Received response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response from add_to_cart:', data);
        if (data.success) {
            window.location.href = '/order/';
        } else {
            alert('Ошибка при добавлении товара в корзину');
        }
    })
    .catch(error => {
        alert('Ошибка при добавлении товара в корзину');
        console.error('Error in addToCart fetch:', error);
    });
}

function updateCartItemQuantity(productId, quantity, quantitySpan, priceDiv) {
    fetch(`/update_cart_item_quantity/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            quantitySpan.textContent = data.quantity;
            priceDiv.textContent = `${data.item_total_price} ₽ x ${data.quantity}`;
            // Обновляем общую сумму корзины
            const totalPriceElem = document.querySelector('.cart-summary h3');
            if (totalPriceElem) {
                totalPriceElem.textContent = `Итого: ${data.total_price} ₽`;
            }
        } else {
            alert('Ошибка при обновлении количества товара');
        }
    })
    .catch(error => {
        alert('Ошибка при обновлении количества товара');
        console.error('Error in updateCartItemQuantity fetch:', error);
    });
}

window.addToCart = addToCart;

// Функция для получения CSRF токена из cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    if (!cookieValue) {
        const meta = document.querySelector('meta[name="csrfmiddlewaretoken"]');
        if (meta) {
            cookieValue = meta.getAttribute('content');
        }
    }
    return cookieValue;
}
