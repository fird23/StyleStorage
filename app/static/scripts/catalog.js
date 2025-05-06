document.addEventListener('DOMContentLoaded', function() {
    // Модальное окно
    const modal = document.getElementById('productModal');
    const modalContent = document.getElementById('modal-content');
    
    document.querySelectorAll('.details-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const productId = this.dataset.productId;
            try {
                const response = await fetch(`/product/${productId}/modal/`);
                modalContent.innerHTML = await response.text();
                modal.style.display = 'flex';
            } catch (error) {
                console.error('Ошибка:', error);
            }
        });
    });

    // Закрытие модального окна
    modal.querySelector('.close').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Добавление в корзину
    document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            
            try {
                const response = await fetch(`/cart/add/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({quantity: 1})
                });
                
                if (response.ok) {
                    alert('Товар добавлен в корзину!');
                    // Обновляем количество товаров в корзине
                    const cartCountElem = document.getElementById('cart-count');
                    if (cartCountElem) {
                        // Запросим текущее количество товаров в корзине с сервера
                        fetch('/cart/count/')
                            .then(res => res.json())
                            .then(data => {
                                if (data.count !== undefined) {
                                    cartCountElem.textContent = data.count;
                                }
                            })
                            .catch(err => console.error('Ошибка при обновлении количества в корзине:', err));
                    }
                }
            } catch (error) {
                console.error('Ошибка:', error);
            }
        });
    });
});

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
        // Попытка получить CSRF токен из meta-тега
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) {
            cookieValue = meta.getAttribute('content');
        }
    }
    return cookieValue;
}

