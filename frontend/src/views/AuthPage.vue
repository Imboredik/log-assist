<template>
  <div class="auth-container" :class="{ 'night-mode': uiStore.isNightMode }">
    <div class="auth-card" :class="{ 'register-mode': activeTab === 'register' }">
      <div class="auth-header">
        <h1>{{ activeTab === 'login' ? 'Вход' : step === 1 ? 'Регистрация' : 'Выбор роли' }}</h1>
        <button class="theme-toggle" @click="uiStore.toggleNightMode">
          <Icon :icon="uiStore.isNightMode ? 'mdi:weather-sunny' : 'mdi:weather-night'" width="24" height="24" />
        </button>
      </div>

      <div v-if="uiStore.message" class="message" :class="{ error: uiStore.isError, success: !uiStore.isError }">
        {{ uiStore.message }}
      </div>

      <form v-if="activeTab === 'login'" @submit.prevent="submitForm" class="auth-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="example@mail.ru"
            required
            title="Введите корректный email, например: example@mail.ru"
          >
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Введите пароль"
            required
            minlength="6"
            title="Пароль должен содержать минимум 6 символов"
          >
        </div>

        <div class="forgot-password">
          <button type="button" class="forgot-password-btn">Забыли пароль?</button>
        </div>

        <div class="form-actions">
          <button type="submit" class="auth-button primary">
            Войти
          </button>
          
          <div class="secondary-actions">
            <button 
              type="button" 
              class="auth-button text-button"
              @click="activeTab = 'register'"
            >
              Зарегистрироваться
            </button>
          </div>
        </div>
      </form>

      <form v-if="activeTab === 'register' && step === 1" @submit.prevent="nextStep" class="auth-form">
        <div class="form-group">
          <label for="username">Имя пользователя</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder="Введите ваше имя"
            required
            title="Используйте только буквы и цифры"
          >
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="example@mail.ru"
            required
            title="Введите корректный email, например: example@mail.ru"
          >
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Введите пароль"
            required
            minlength="6"
            title="Пароль должен содержать минимум 6 символов"
          >
        </div>

        <div class="form-group">
          <label for="password_confirmation">Подтверждение пароля</label>
          <input
            id="password_confirmation"
            v-model="form.password_confirmation"
            type="password"
            placeholder="Повторите пароль"
            required
            minlength="6"
            title="Пароли должны совпадать"
          >
        </div>

        <div class="form-actions">
          <button type="submit" class="auth-button primary">
            Далее
          </button>
          
          <div class="secondary-actions">
            <button 
              type="button" 
              class="auth-button text-button"
              @click="activeTab = 'login'"
            >
              Уже есть аккаунт? Войти
            </button>
          </div>
        </div>
      </form>

      <div v-if="activeTab === 'register' && step === 2" class="step-2-container">
        <div class="role-selection">
          <h3>Выберите вашу роль</h3>
          <div class="role-options">
            <div 
              v-for="role in availableRoles" 
              :key="role.id" 
              class="role-card"
              :class="{ 'selected': form.role_id === role.id }"
              @click="form.role_id = role.id"
            >
              <h4>{{ role.role }}</h4>
              <p>{{ role.description }}</p>
            </div>
          </div>
        </div>
        
        <div class="form-actions">
          <button 
            type="button" 
            class="auth-button primary"
            @click="submitForm"
            :disabled="!form.role_id"
          >
            Зарегистрироваться
          </button>
          <button 
            type="button" 
            class="auth-button text-button"
            @click="step = 1"
          >
            Назад
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth.store'
import { useUIStore } from '@/stores/ui.store'
import api from '@/composables/useApi'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const activeTab = ref(route.params.initialTab || 'login')
const step = ref(1)

const form = ref({
  username: '',
  email: '',
  password: '',
  password_confirmation: '',
  role_id: null
})

const availableRoles = ref([])

onMounted(async () => {
  try {
    // Проверяем, открыто ли через расширение
    const urlParams = new URLSearchParams(window.location.search);
    const isExtensionRequest = urlParams.get('extension') === 'true';
    
    if (isExtensionRequest) {
      // Проверяем авторизацию
      const isAuthenticated = await authStore.checkAuth();
      
      if (isAuthenticated && authStore.token) {
        // Если уже авторизован, сразу отправляем токен
        await sendTokenToExtension(authStore.token);
        return;
      }
    }
    
    const response = await api.getRoles()
    availableRoles.value = response.data.map(role => ({
      id: role.id,
      role: role.role,
      description: role.description || 'Описание роли отсутствует'
    }))
  } catch (error) {
    console.error('Ошибка при получении ролей:', error)
  }
})

const nextStep = () => {
  if (!form.value.username || !form.value.email || !form.value.password || !form.value.password_confirmation) {
    uiStore.showMessage('Пожалуйста, заполните все поля', true)
    return
  }
  
  if (form.value.password !== form.value.password_confirmation) {
    uiStore.showMessage('Пароли не совпадают', true)
    return
  }
  
  if (form.value.password.length < 6) {
    uiStore.showMessage('Пароль должен содержать минимум 6 символов', true)
    return
  }
  
  step.value = 2
}

const handleError = (error) => {
  console.error('Ошибка:', error)
  
  // Ошибки, которые мы показываем пользователю
  const userFriendlyMessages = {
    // Логин
    'Неверный email или пароль': 'Неверный email или пароль',
    'Пользователя с таким email не существует': 'Неверный email или пароль',
    
    // Регистрация
    'Пользователь с такой почтой уже зарегистрирован': 'Пользователь с таким email уже существует',
    'Пользователь с подобным именем уже зарегистрирован': 'Имя пользователя уже занято',
    'Пароли не совпадают': 'Пароли не совпадают',
    'Пароль должен содержать минимум 6 символов': 'Пароль должен содержать минимум 6 символов',
    'Email слишком большой': 'Email слишком длинный',
    'Пожалуйста, заполните все поля': 'Пожалуйста, заполните все поля',
    'Пожалуйста, выберите роль': 'Пожалуйста, выберите роль',
    'Указанная роль не существует': 'Выбрана недопустимая роль'
  }

  // Ошибки сервера, которые логируем но не показываем пользователю
  const serverErrors = [
    'Failed to fetch',
    'Network Error',
    'Request failed with status code 500',
    'Request failed with status code 502',
    'Request failed with status code 503',
    'Request failed with status code 504'
  ]

  // Определяем тип ошибки
  let errorMessage = error.message || 'Произошла ошибка, попробуйте снова'
  
  // Проверяем, есть ли сообщение об ошибке в ответе сервера
  if (error.response?.data?.detail) {
    errorMessage = error.response.data.detail
  }

  // Для ошибок сервера показываем общее сообщение
  if (serverErrors.some(serverError => errorMessage.includes(serverError))) {
    console.error('Server error:', error)
    return 'Ошибка сервера. Попробуйте позднее'
  }

  // Для ошибок валидации показываем понятное сообщение
  if (errorMessage in userFriendlyMessages) {
    return userFriendlyMessages[errorMessage]
  }

  // Для остальных ошибок показываем общее сообщение
  console.error('Unknown error:', error)
  return 'Произошла ошибка, попробуйте снова'
}

const submitForm = async () => {
  uiStore.showMessage(null)
  
  try {
    if (activeTab.value === 'login') {
      if (!form.value.email || !form.value.password) {
        throw new Error('Пожалуйста, заполните все поля')
      }
      
      await authStore.login({
        email: form.value.email,
        password: form.value.password
      })
      
      const urlParams = new URLSearchParams(window.location.search);
      const isExtensionRequest = urlParams.get('extension') === 'true';
      
      if (isExtensionRequest) {
        await new Promise((resolve) => {
          const listener = (event) => {
            if (event.data?.type === "ASSIST_LOG_AUTH_ACK") {
              window.removeEventListener("message", listener);
              resolve();
            }
          };
          window.addEventListener("message", listener);
          
          setTimeout(() => {
            window.removeEventListener("message", listener);
            resolve();
          }, 2000);
        });
      }
    } else {
      if (step.value === 1) {
        nextStep()
        return
      }

      if (!form.value.role_id) {
        throw new Error('Пожалуйста, выберите роль')
      }
      
      await authStore.register({
        username: form.value.username,
        email: form.value.email,
        password: form.value.password,
        role_id: form.value.role_id
      })
      
      uiStore.showMessage('Регистрация прошла успешно', false)
      
      const urlParams = new URLSearchParams(window.location.search)
      const isExtensionRequest = urlParams.get('extension') === 'true'
      if (!isExtensionRequest) {
        setTimeout(() => {
          activeTab.value = 'login'
          step.value = 1
        }, 2000)
      }
    }
  } catch (err) {
    // Сначала возвращаемся на шаг назад для регистрации
    if (activeTab.value === 'register' && step.value === 2) {
      step.value = 1
      await nextTick()
    }
    
    const userFriendlyMessage = handleError(err)
    uiStore.showMessage(userFriendlyMessage, true)
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--color-background);
  transition: background-color 0.3s ease;
  padding: 20px;
}

.auth-card {
  width: 340px;
  min-height: 400px;
  background-color: var(--panel-bg);
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 30px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border: 1px solid var(--color-border);
}

.auth-card.register-mode {
  min-height: 500px;
}

.auth-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.auth-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #7800FF;
  margin: 0;
}

.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text);
  transition: color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.theme-toggle:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.message {
  padding: 10px;
  border-radius: 15px;
  margin-bottom: 15px;
  font-size: 13px;
  text-align: center;
  animation: fadeIn 0.3s ease;
}

.message.error {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ef9a9a;
}

.message.success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.auth-form {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  color: var(--color-text);
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--input-border);
  border-radius: 15px;
  font-size: 14px;
  transition: all 0.3s ease;
  background-color: var(--input-bg);
  color: var(--color-text); 
}

.form-group input::placeholder {
  color: var(--input-placeholder);
  opacity: 1; 
}

.form-group input:focus {
  border-color: #7800FF; 
  outline: none;
  box-shadow: 0 0 0 2px rgba(120, 0, 255, 0.2);
}

.forgot-password {
  text-align: left;
  margin-bottom: 15px;
}

.forgot-password-btn {
  background: none;
  border: none;
  color: #7800FF;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
  text-decoration: none;
}

.form-actions {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.auth-button {
  padding: 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.auth-button.primary {
  background-color: #7800FF;
  color: white;
  border: none;
}

.auth-button.primary:hover {
  background-color: #1a2a3a;
}

.auth-button.primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.secondary-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.auth-button.text-button {
  background: none;
  border: none;
  color: #7800FF;
  padding: 0;
  font-size: 13px;
  text-align: left;
}

.auth-button.text-button:hover {
  text-decoration: underline;
}

.step-2-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.role-selection {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.role-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.role-card {
  padding: 20px;
  border-radius: 15px;
  border: 1px solid var(--input-border);
  background-color: var(--input-bg);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 10px;
}

.role-card:hover {
  border-color: #7800FF;
}

.role-card.selected {
  border-color: #7800FF;
  background-color: rgba(120, 0, 255, 0.1);
}

.role-card h4 {
  margin: 0;
  color: #7800FF;
}

.role-card p {
  margin: 0;
  font-size: 14px;
  color: var(--color-text);
}
</style>