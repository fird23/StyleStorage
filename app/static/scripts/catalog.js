document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('productModal');
    const removeItemModal = document.getElementById('removeItemModal');
    const confirmRemoveItemBtn = document.getElementById('confirmRemoveItemBtn');
    const cancelRemoveItemBtn = document.getElementById('cancelRemoveItemBtn');
    const removeItemModalClose = document.getElementById('removeItemModalClose');

    function openProductModal(productId) {
        console.log('Клик на кнопку Подробнее, productId:', productId);
        fetch(`/product/${productId}/modal/`)
            .then(response => response.json())
            .then(product => {
                console.log('Данные товара получены:', product);
                document.getElementById('modal-product-name').textContent = product.name;
                document.getElementById('modal-product-image').src = product.image_url;
                document.getElementById('modal-product-image').alt = product.name;
                document.getElementById('modal-product-description').textContent = product.description;
                document.getElementById('modal-product-material').textContent = product.material;
                document.getElementById('modal-product-category').textContent = product.category_display;
                document.getElementById('modal-product-dimensions').textContent = product.dimensions;
                document.getElementById('modal-product-price').textContent = product.price;
                modal.style.display = 'flex';

                // Set productId on modal add to cart button
                const modalAddToCartBtn = modal.querySelector('#modal-add-to-cart');
                if (modalAddToCartBtn) {
                    modalAddToCartBtn.setAttribute('data-product-id', productId);
                }
            })
            .catch(error => {
                console.error('Ошибка загрузки данных товара:', error);
            });
    }

    function closeProductModal() {
        if (modal) {
            modal.style.display = 'none';
        }
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

        // Закрытие модального окна при клике на фон
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeProductModal();
            }
        });
    }

    // Обработчик клика для кнопок "Добавить в корзину" (включая модальное окно)
    document.querySelectorAll('.btn-cart').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.getAttribute('data-product-id');
            if (productId) {
                addToCart(productId);
            }
        });
    });

    let productIdToRemove = null;
    let cartItemToRemove = null;

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
            if (!productId || !quantitySpan) return;

            let currentQuantity = parseInt(quantitySpan.textContent);
            if (isNaN(currentQuantity)) currentQuantity = 1;

            if (button.classList.contains('plus')) {
                currentQuantity += 1;
                updateCartItemQuantity(productId, currentQuantity);
                button.blur();
            } else if (button.classList.contains('minus')) {
                if (currentQuantity > 1) {
                    currentQuantity -= 1;
                    updateCartItemQuantity(productId, currentQuantity);
                    button.blur();
                } else {
                    console.log('Quantity is 1, showing confirmation modal');
                    // Show confirmation modal to remove item
                    productIdToRemove = productId;
                    cartItemToRemove = cartItemDiv;
                    if (removeItemModal) {
                        removeItemModal.style.display = 'flex';
                    }
                }
            }
        });
    }

    if (confirmRemoveItemBtn) {
        confirmRemoveItemBtn.addEventListener('click', () => {
            if (productIdToRemove && cartItemToRemove) {
                removeCartItem(productIdToRemove, cartItemToRemove);
            }
            if (removeItemModal) {
                removeItemModal.style.display = 'none';
            }
            productIdToRemove = null;
            cartItemToRemove = null;
        });
    }

    if (cancelRemoveItemBtn) {
        cancelRemoveItemBtn.addEventListener('click', () => {
            if (removeItemModal) {
                removeItemModal.style.display = 'none';
            }
            productIdToRemove = null;
            cartItemToRemove = null;
        });
    }

    if (removeItemModalClose) {
        removeItemModalClose.addEventListener('click', () => {
            if (removeItemModal) {
                removeItemModal.style.display = 'none';
            }
            productIdToRemove = null;
            cartItemToRemove = null;
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

function removeCartItem(productId, cartItemDiv) {
    fetch(`/remove_from_cart/${productId}/`, {
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
        if (data.success) {
            // Remove the cart item from the DOM
            if (cartItemDiv && cartItemDiv.parentNode) {
                cartItemDiv.parentNode.removeChild(cartItemDiv);
            }
            // Optionally update total price or reload page
            window.location.reload();
        } else {
            alert('Ошибка при удалении товара из корзины');
        }
    })
    .catch(error => {
        alert('Ошибка при удалении товара из корзины');
        console.error('Error in removeCartItem fetch:', error);
    });
}

function updateCartItemQuantity(productId, quantity) {
    fetch(`/update_cart_item_quantity/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`,
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            const cartItemDiv = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
            if (cartItemDiv) {
                const quantitySpan = cartItemDiv.querySelector('.quantity');
                if (quantitySpan) {
                    quantitySpan.textContent = data.quantity;
                }
                const itemTotalPriceElem = cartItemDiv.querySelector('.item-total-price');
                if (itemTotalPriceElem) {
                    itemTotalPriceElem.textContent = `${data.item_total_price.toFixed(2)} ₽`;
                }
            }
            const totalPriceElem = document.querySelector('.cart-summary h3');
            if (totalPriceElem) {
                totalPriceElem.textContent = `Итого: ${data.total_price} ₽`;
            }
        } else {
            console.error('Ошибка при обновлении количества товара:', data);
        }
    })
    .catch(error => {
        alert('Ошибка при обновлении количества товара');
        console.error('Error in updateCartItemQuantity fetch:', error);
    });
}

window.addToCart = addToCart;

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
