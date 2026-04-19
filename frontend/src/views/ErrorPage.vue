<template>
  <div class="app-interface">
    <!-- Шапка приложения -->
    <header class="app-header">
      <div class="header-content">
        <button class="back-button" @click="goBack">
          <Icon icon="mdi:arrow-left" width="24" height="24" />
        </button>
        <h1>Мой Профиль</h1>
        <nav class="app-nav">
          <a href="#" @click.prevent="navError">Профиль</a>
          <a href="#" @click.prevent="navError">Настройки</a>
          <a href="#" @click.prevent="navError">Сообщения</a>
        </nav>
      </div>
    </header>

    <!-- Основной контент -->
    <main class="app-content">
      <!-- Форма входа -->
      <section class="card login-form">
        <h2>Вход в систему</h2>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>Email</label>
            <input 
              type="email" 
              placeholder="Введите ваш email"
              @focus="generateFocusError"
            >
          </div>
          <div class="form-group">
            <label>Пароль</label>
            <input 
              type="password" 
              placeholder="Введите пароль"
              @input="generateInputError"
            >
          </div>
          <button type="submit" class="submit-btn">Войти</button>
          <a href="#" @click.prevent="forgotPassword" class="forgot-link">Забыли пароль?</a>
        </form>
      </section>

      <!-- Галерея изображений -->
      <section class="card image-gallery">
        <h2>Мои фотографии</h2>
        <div class="gallery-grid">
          <div 
            v-for="n in 4" 
            :key="n" 
            class="gallery-item"
            @click="openImage(n)"
          >
            <div class="image-placeholder"></div>
            <span>Фото {{ n }}</span>
          </div>
        </div>
      </section>

      <!-- Форма обратной связи -->
      <section class="card feedback-form">
        <h2>Обратная связь</h2>
        <form @submit.prevent="submitFeedback">
          <div class="form-group">
            <label>Тема</label>
            <select v-model="feedbackTopic" @change="generateSelectError">
              <option value="">Выберите тему</option>
              <option value="bug">Сообщить об ошибке</option>
              <option value="suggestion">Предложение</option>
              <option value="other">Другое</option>
            </select>
          </div>
          <div class="form-group">
            <label>Сообщение</label>
            <textarea 
              placeholder="Введите ваше сообщение"
              @keydown="generateTextareaError"
            ></textarea>
          </div>
          <button type="submit" class="submit-btn">Отправить</button>
        </form>
      </section>

      <!-- Уведомление о cookies -->
      <div class="cookie-notice" v-if="showCookieNotice">
        <p>Мы используем cookies для улучшения вашего опыта</p>
        <button @click="acceptCookies" class="cookie-btn">Принять</button>
        <button @click="rejectCookies" class="cookie-btn">Отклонить</button>
      </div>
    </main>

    <!-- Футер -->
    <footer class="app-footer">
      <p>&copy; 2023 Моё Приложение. Все права защищены.</p>
      <div class="footer-links">
        <a href="#" @click.prevent="footerLinkError">Политика конфиденциальности</a>
        <a href="#" @click.prevent="footerLinkError">Условия использования</a>
        <a href="#" @click.prevent="footerLinkError">Контакты</a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()
const showCookieNotice = ref(true)
const feedbackTopic = ref('')

const goBack = () => {
  router.go(-1)
}

const navError = () => {
  console.error("NavigationError: страница временно недоступна")
  alert('Извините, этот раздел временно недоступен')
}

const submitForm = () => {
  try {
    // Имитация ошибки аутентификации
    const invalidData = JSON.parse('{"token": "invalid"}')
    console.log(invalidData.nonexistent.property)
  } catch (e) {
    console.error("AuthError: ошибка аутентификации", e)
    alert('Ошибка входа. Пожалуйста, попробуйте позже.')
  }
}

const forgotPassword = () => {
  try {
    window.location.href = "https://example.com/reset?token=" + undefinedVariable
  } catch (e) {
    console.error("PasswordResetError: ошибка сброса пароля", e)
    alert('Сервис восстановления пароля временно недоступен')
  }
}

const openImage = (id) => {
  try {
    const gallery = document.querySelectorAll('.gallery-item')
    gallery[id].style.transform = 'scale(1.5)'
  } catch (e) {
    console.error("GalleryError: ошибка открытия изображения", e)
    alert('Не удалось открыть изображение')
  }
}

const submitFeedback = () => {
  try {
    const invalidFunction = null
    invalidFunction()
  } catch (e) {
    console.error("FeedbackError: ошибка отправки формы", e)
    alert('Не удалось отправить сообщение. Пожалуйста, попробуйте позже.')
  }
}

const acceptCookies = () => {
  try {
    localStorage.setItem('cookiesAccepted', true)
    showCookieNotice.value = false
    new ArrayBuffer(Number.MAX_SAFE_INTEGER)
  } catch (e) {
    console.error("CookieError: ошибка обработки cookies", e)
    showCookieNotice.value = false
  }
}

const rejectCookies = () => {
  try {
    localStorage.setItem('cookiesAccepted', false)
    showCookieNotice.value = false
    decodeURIComponent('%')
  } catch (e) {
    console.error("CookieError: ошибка обработки cookies", e)
    showCookieNotice.value = false
  }
}

const footerLinkError = () => {
  try {
    const links = document.querySelectorAll('.footer-links a')
    links.forEach(link => link.style.color = undefinedColor)
  } catch (e) {
    console.error("FooterLinkError: ошибка перехода по ссылке", e)
    alert('Эта страница временно недоступна')
  }
}

const generateFocusError = () => {
  try {
    const inputs = document.querySelectorAll('input')
    inputs[0].style.borderColor = invalidColor
  } catch (e) {
    console.error("FocusError: ошибка при фокусировке", e)
  }
}

const generateInputError = () => {
  try {
    const event = new Event('invalidEvent')
    window.dispatchEvent(event)
  } catch (e) {
    console.error("InputError: ошибка ввода", e)
  }
}

const generateSelectError = () => {
  try {
    const select = document.querySelector('select')
    select.options[select.selectedIndex].value = undefined
  } catch (e) {
    console.error("SelectError: ошибка выбора", e)
  }
}

const generateTextareaError = () => {
  try {
    const textarea = document.querySelector('textarea')
    textarea.value = textarea.value.repeat(1000000)
  } catch (e) {
    console.error("TextareaError: ошибка ввода текста", e)
  }
}
</script>

<style scoped>
.app-interface {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
}

.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
  position: relative;
}

.back-button {
  background: none;
  border: none;
  cursor: pointer;
  color: white;
  transition: color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  padding: 0;
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 24px;
  flex-grow: 1;
}

.app-nav {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}

.app-nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
}

.app-nav a:hover {
  text-decoration: underline;
}

.app-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.card h2 {
  margin-top: 0;
  font-size: 20px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.submit-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
}

.submit-btn:hover {
  background-color: #2980b9;
}

.forgot-link {
  display: inline-block;
  margin-top: 10px;
  color: #3498db;
  text-decoration: none;
  font-size: 14px;
}

.forgot-link:hover {
  text-decoration: underline;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.gallery-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.gallery-item:hover {
  transform: scale(1.03);
}

.image-placeholder {
  height: 120px;
  background-color: #f1f2f6;
  border-radius: 4px;
  margin-bottom: 5px;
}

.cookie-notice {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #2c3e50;
  color: white;
  padding: 15px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 15px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.cookie-notice p {
  margin: 0;
}

.cookie-btn {
  background-color: transparent;
  color: white;
  border: 1px solid white;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.cookie-btn:hover {
  background-color: rgba(255,255,255,0.1);
}

.app-footer {
  text-align: center;
  padding: 20px;
  background-color: #f1f2f6;
  border-radius: 8px;
}

.footer-links {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.footer-links a {
  color: #3498db;
  text-decoration: none;
  font-size: 14px;
}

.footer-links a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .app-content {
    grid-template-columns: 1fr;
  }
  
  .gallery-grid {
    grid-template-columns: 1fr;
  }
  
  .cookie-notice {
    flex-direction: column;
    text-align: center;
  }
}
</style>