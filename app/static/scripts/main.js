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
  return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
  const cardNumber = document.getElementById('card-number');
  const expDate = document.getElementById('exp-date');
  const cvv = document.getElementById('cvv');

  if (cardNumber) {
    cardNumber.addEventListener('input', function(e) {
      let value = e.target.value.replace(/\D/g, '');
      value = value.substring(0, 16);
      let formatted = value.replace(/(\d{4})(?=\d)/g, '$1 ');
      e.target.value = formatted;
      if (value.length === 16) expDate.focus();
    });
    cardNumber.addEventListener('keydown', function(e) {
      if (e.key === 'Backspace' && e.target.value.endsWith(' ')) {
        e.target.value = e.target.value.slice(0, -1);
      }
    });
  }

  if (expDate) {
    expDate.addEventListener('input', function(e) {
      let value = e.target.value.replace(/\D/g, '');
      let formatted = value.substring(0, 4);
      if (formatted.length > 2) {
        formatted = formatted.substring(0, 2) + '/' + formatted.substring(2);
      }
      e.target.value = formatted;
      if (value.length === 4) cvv.focus();
    });

    expDate.addEventListener('keydown', function(e) {
      if (e.key === 'Backspace' && e.target.value.endsWith('/')) {
        e.target.value = e.target.value.slice(0, -1);
      }
    });
  }

  if (cvv) {
    cvv.addEventListener('input', function(e) {
      e.target.value = e.target.value.replace(/\D/g, '').substring(0, 3);
    });
  }

  // Функции для модального окна редактирования профиля
  const modal = document.getElementById('editModal');
  let modalContent = null;
  if (modal) {
      modalContent = modal.querySelector('.modal-content');

      window.openEditModal = function() {
          modal.style.display = 'flex';
      };

      window.closeEditModal = function() {
          modal.style.display = 'none';
      };

      // Закрытие модального окна при клике вне его содержимого
      window.addEventListener('click', function(event) {
          if (event.target === modal) {
              closeEditModal();
          }
      });
  }

  // Добавляем код для переключения гамбургер-меню с кнопкой закрытия и затемнением
  const hamburger = document.querySelector('.hamburger');
  const navList = document.querySelector('.nav-list');
  const burgerCloseBtn = document.getElementById('burgerCloseBtn');
  const burgerOverlay = document.getElementById('burgerOverlay');
  const menuOverlay = document.querySelector('.menu-overlay');

  if (hamburger && navList && burgerCloseBtn && burgerOverlay && menuOverlay) {
      hamburger.addEventListener('click', function () {
          hamburger.classList.toggle('active');
          navList.classList.toggle('active');
          if (navList.classList.contains('active')) {
              burgerCloseBtn.style.display = 'block';
              burgerOverlay.classList.add('active');
              menuOverlay.classList.add('active');
          } else {
              burgerCloseBtn.style.display = 'none';
              burgerOverlay.classList.remove('active');
              menuOverlay.classList.remove('active');
          }
      });

      burgerCloseBtn.addEventListener('click', function () {
          hamburger.classList.remove('active');
          navList.classList.remove('active');
          burgerCloseBtn.style.display = 'none';
          burgerOverlay.classList.remove('active');
          menuOverlay.classList.remove('active');
      });

      burgerOverlay.addEventListener('click', function () {
          hamburger.classList.remove('active');
          navList.classList.remove('active');
          burgerCloseBtn.style.display = 'none';
          burgerOverlay.classList.remove('active');
          menuOverlay.classList.remove('active');
      });
  }
});
