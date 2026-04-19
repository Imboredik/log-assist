<template>
  <div v-if="menuStore.isOpen" class="Menu-overlay" @click.self="close">
    <div class="Menu">
      <div class="Menu-sidebar">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="menuStore.setActiveTab(tab.id)"
          :class="{ active: menuStore.activeTab === tab.id }"
        >
          <Icon :icon="tab.icon" width="20" height="20" />
          <span>{{ tab.label }}</span>
        </button>
      </div>
      
      <div class="Menu-content">
        <button class="close-btn" @click="close">
          <Icon icon="mdi:close" width="24" height="24" />
        </button>
        
        <!-- Профиль -->
        <transition name="fade-slide" mode="out-in">
          <div v-if="menuStore.activeTab === 'profile'" class="profile-tab" key="profile">
            <transition name="fade-slide" mode="out-in">
              <div v-if="!isEditingProfile" class="profile-view" key="view">
                <div class="profile-header">
                  <div 
                    class="profile-avatar" 
                    :style="{ 
                      backgroundImage: authStore.user.avatarUrl ? `url(${authStore.user.avatarUrl})` : 'none',
                      backgroundColor: !authStore.user.avatarUrl ? '#ddd' : 'transparent'
                    }"
                  ></div>
                  <h2>{{ authStore.user.name }}</h2>
                  <div class="profile-email">{{ authStore.user.email }}</div>
                </div>
                <button class="edit-profile-btn secondary-btn" @click="isEditingProfile = true">
                  <Icon icon="mdi:pencil-outline" width="16" height="16" />
                  Редактировать профиль
                </button>
              </div>
              <ProfileEditor 
                v-else 
                :user="authStore.user" 
                @cancel="isEditingProfile = false" 
                @saved="isEditingProfile = false"
                key="editor"
              />
            </transition>
          </div>

          <!-- Подписка -->
          <div v-else-if="menuStore.activeTab === 'subscription'" class="subscription-tab" key="subscription">
              <h2>Подписка</h2>
              <div class="subscription-plans">
                  <div 
                  v-for="(plan, id) in uiStore.subscription.plans" 
                  :key="id"
                  :class="['plan-card', { 'active': uiStore.subscription.currentPlan === id }]"
                  >
                  <h3>{{ plan.name }}</h3>
                  <div class="price">
                      {{ plan.price === 0 ? 'Бесплатно' : `${plan.price} ₽/мес` }}
                      </div>
                      <ul class="features">
                          <li v-for="(feature, index) in plan.features" :key="index">
                          {{ feature }}
                          </li>
                      </ul>
                      <button 
                      @click="selectPlan(id)"
                      :class="['select-btn', { 'selected': uiStore.subscription.currentPlan === id }]"
                      >
                      {{ uiStore.subscription.currentPlan === id ? 'Выбрано' : 'Выбрать' }}
                      </button>
                  </div>
              </div>
          </div>
          
          <!-- Расширение -->
          <div v-else-if="menuStore.activeTab === 'extension'" class="extension-tab" key="extension">
            <div class="guide-header">
              <h1>Инструкция по установке</h1>
              <a href="/extension.zip" class="download-button">Скачать расширение (.zip)</a>
              <router-link to="/error" class="download-button test-button">Тестовая страница</router-link>
            </div>
            
            <div class="guide-steps">
              <div class="step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <h3>Установка в режиме разработчика</h3>
                  <p>Откройте Chrome и перейдите на страницу <code>chrome://extensions</code></p>
                  <p>Включите режим разработчика в правом верхнем углу</p>
                  <p>Нажмите "Загрузить распакованное расширение" и выберите папку с распакованным архивом</p>
                </div>
              </div>
              
              <div class="step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <h3>Использование</h3>
                  <p>После установки нажмите на иконку расширения в панели инструментов</p>
                  <p>Авторизуйтесь или зарегистрируйтесь, если вы впервые используете сервис</p>
                  <p>Следуйте инструкциям на панели расширения</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Настройки -->
          <div v-else-if="menuStore.activeTab === 'settings'" class="settings-tab" key="settings">
            <h2>Настройки</h2>
            <div class="setting-item">
              <label>Тема сайта</label>
              <button @click="toggleTheme" class="theme-toggle">
                <Icon :icon="uiStore.isNightMode ? 'mdi:weather-sunny' : 'mdi:weather-night'" width="20" height="20" />
                {{ uiStore.isNightMode ? 'Дневной режим' : 'Ночной режим' }}
              </button>
            </div>
            <div class="setting-item">
              <label>Отображение изображений</label>
              <DropdownMenu 
              :items="imageDisplayItems" 
              align="left"
              @item-click="handleImageDisplayChange"
            >
              <template #trigger>
                <button class="settings-button">
                  <Icon :icon="imageDisplayMode === 'image' ? 'mdi:image' : 'mdi:file-document-outline'" width="20" />
                  <span>{{ imageDisplayMode === 'image' ? 'Как изображения' : 'Как файлы' }}</span>
                </button>
              </template>
            </DropdownMenu>
            </div>
          </div>
          
          <!-- Тикеты -->
        <div v-else-if="menuStore.activeTab === 'tickets'" class="tickets-tab" key="tickets">
          <div class="tickets-header">
            <h2>Тикеты</h2>
            <div class="tickets-actions">
              <button class="new-ticket-btn" @click="ticketStore.openChatSelection">
                Новый тикет
              </button>
              <DropdownMenu 
                :items="sortOptions"
                @item-click="handleSortClick"
                align="right"
                trigger="click"
              >
                <template #trigger>
                  <button class="sort-button">
                    {{ currentSortLabel }}
                    <Icon 
                      v-if="currentSort.field" 
                      :icon="currentSort.direction === 'asc' ? 'heroicons-solid:sort-ascending' : 'heroicons-solid:sort-descending'" 
                      width="16" 
                      height="16" 
                    />
                  </button>
                </template>
              </DropdownMenu>
            </div>
          </div>
          
          <transition name="fade-slide" mode="out-in">
            <!-- Выбор чата -->
            <ChatSelection 
              v-if="ticketStore.isChatSelectionOpen"
              @saved="ticketStore.isChatSelectionOpen = false"
              @cancel="ticketStore.isChatSelectionOpen = false"
            />
            
            <!-- Редактор тикета -->
            <TicketEditor
              v-else-if="ticketStore.isEditorOpen"
              @saved="ticketStore.isEditorOpen = false"
              @cancel="ticketStore.isEditorOpen = false"
            />
            
            <!-- Просмотр тикета -->
            <TicketView
              v-else-if="ticketStore.currentTicket?.id && !ticketStore.isEditorOpen"
            />
            
            <!-- Список тикетов -->
            <div v-else class="tickets-list">
              <div v-if="ticketStore.isLoading" class="loading">
                <Icon icon="mdi:loading" class="spin" /> Загрузка...
              </div>
              
              <div v-else-if="ticketStore.tickets.length === 0" class="empty-tickets">
                У вас пока нет тикетов
              </div>
              
              <div v-else class="ticket-items">
                <TicketButton 
                  v-for="ticket in ticketStore.tickets"
                  :key="ticket.id"
                  :ticket="ticket"
                  :is-active="ticketStore.currentTicket?.id === ticket.id"
                  @ticket-selected="ticketStore.openTicketView(ticket.id)"
                />
              </div>
            </div>
          </transition>
        </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth.store'
import { useUIStore } from '@/stores/ui.store'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat.store'
import { useMenuStore } from '@/stores/menu.store'
import { useTicketStore } from '@/stores/ticket.store'
import ChatSelection from './ChatSelection.vue'
import TicketEditor from './TicketEditor.vue'
import TicketView from '@/views/TicketView.vue'
import ProfileEditor from './ProfileEditor.vue'
import TicketButton from './TicketButton.vue'
import DropdownMenu from './DropdownMenu.vue'

const menuStore = useMenuStore()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()
const chatStore = useChatStore()
const ticketStore = useTicketStore()
const isEditingProfile = ref(false)
const imageDisplayMode = ref('image')

watch([() => menuStore.isOpen, () => menuStore.activeTab], async ([isOpen, activeTab]) => {
  if (isOpen && activeTab === 'tickets') {
    await ticketStore.fetchTickets()
    applySorting() 
  }
}, { immediate: true })


const imageDisplayItems = ref([
  {
    label: 'Как изображения',
    icon: 'mdi:image',
    action: 'image',
    hoverBgColor: '#7800FF',
    hoverTextColor: 'white'
  },
  {
    label: 'Как файлы',
    icon: 'mdi:file-document-outline',
    action: 'file',
    hoverBgColor: '#7800FF',
    hoverTextColor: 'white'
  }
])

const handleImageDisplayChange = (item) => {
  imageDisplayMode.value = item.action
  saveImageDisplayMode()
}

const saveImageDisplayMode = () => {
  localStorage.setItem('imageDisplayMode', imageDisplayMode.value)
}

onMounted(() => {
  const savedMode = localStorage.getItem('imageDisplayMode')
  if (savedMode) {
    imageDisplayMode.value = savedMode
  }
})

const sortOptions = ref([
  { label: 'По номеру', action: 'id' },
  { label: 'По приоритету', action: 'priority' },
  { label: 'По дате', action: 'date' }
])

const currentSort = ref({
  field: null,
  direction: null
})

const emit = defineEmits(['close'])

const tabs = [
  { id: 'profile', label: 'Личный кабинет', icon: 'mdi:account-outline' },
  { id: 'subscription', label: 'Подписка', icon: 'mdi:crown-outline' },
  { id: 'extension', label: 'Расширение', icon: 'mdi:puzzle-outline' }, 
  { id: 'settings', label: 'Настройки', icon: 'mdi:cog-outline' },
  { id: 'tickets', label: 'Тикеты', icon: 'mdi:ticket-outline' }
]

const close = () => {
  menuStore.closeMenu()
  isEditingProfile.value = false
  emit('close')
}

const selectPlan = (planId) => {
  uiStore.changeSubscription(planId)
}

const logout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Ошибка при выходе:', error)
  }
}

const currentSortLabel = computed(() => {
  if (!currentSort.value.field) return 'Сортировать по...'
  
  const fieldLabel = sortOptions.value.find(opt => opt.action === currentSort.value.field)?.label || ''
  return fieldLabel
})

const handleSortClick = (item) => {
  if (currentSort.value.field !== item.action) {
    // Новое поле - сортировка по убыванию
    currentSort.value = {
      field: item.action,
      direction: 'desc'
    }
  } else {
    // То же поле - переключаем направление
    if (currentSort.value.direction === 'desc') {
      currentSort.value.direction = 'asc'
    } else {
      // Сброс сортировки при третьем нажатии
      currentSort.value = {
        field: null,
        direction: null
      }
    }
  }
  
  applySorting()
}

const applySorting = () => {
  if (!currentSort.value.field) {
    ticketStore.fetchTickets()
    return
  }
  
  ticketStore.tickets.sort((a, b) => {
    let comparison = 0
    
    switch (currentSort.value.field) {
      case 'id':
        comparison = a.ticket_id - b.ticket_id
        break
      case 'priority':
        comparison = a.priority_id - b.priority_id
        break
      case 'date':
        comparison = new Date(a.date_of_create) - new Date(b.date_of_create)
        break
    }
    
    return currentSort.value.direction === 'asc' ? comparison : -comparison
  })
}

const toggleTheme = () => {
  uiStore.toggleNightMode()
}

</script>

<style scoped>
.Menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.Menu {
  display: flex;
  width: 900px;
  max-width: 90%;
  height: 90vh;
  background-color: var(--panel-bg);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}


.Menu-sidebar {
  width: 220px;
  background-color: var(--sidebar-bg);
  padding: 20px 0;
  border-right: 1px solid var(--color-border);
}

.Menu-sidebar button {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 12px 20px;
  background: none;
  border: none;
  color: var(--color-text);
  font-family: 'RostelecomBasis', sans-serif;
  font-size: 14px;
  cursor: pointer;
  gap: 10px;
  transition: all 0.2s ease;
}

.Menu-sidebar button:hover {
  background-color: var(--chat-button-hover);
}

.Menu-sidebar button.active {
  background-color: var(--chat-button-active);
  color: #7800FF;
}

.Menu-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  position: relative;
  display: flex;
  flex-direction: column;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text);
  opacity: 0.7;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

.profile-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  text-align: center;
}

.profile-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.profile-header {
  text-align: center;
  margin-bottom: 20px;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: #ddd;
  background-size: cover;
  background-position: center;
  margin: 0 auto 15px;
  border: 3px solid var(--color-border);
}

.profile-email {
  color: var(--color-text);
  opacity: 0.8;
  margin: 5px 0;
}

.profile-created {
  font-size: 13px;
  color: var(--color-text);
  opacity: 0.6;
  margin-top: 10px;
}

.edit-profile-btn {
  padding: 10px 20px;
  background-color: transparent;
  color: #7800FF;
  border: 1px solid #7800FF;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  font-size: 14px;
}

.edit-profile-btn:hover {
  background-color: rgba(120, 0, 255, 0.1);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: #ffeeee;
  color: #d32f2f;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: 'RostelecomBasis', sans-serif;
  font-size: 14px;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background-color: #ffdddd;
}

.extension-tab {
  padding: 20px;
}

.guide-header {
  text-align: center;
  margin-bottom: 40px;
}

.download-button {
  display: inline-block;
  padding: 12px 24px;
  background-color: #7800FF;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  margin: 10px 5px;
  transition: background-color 0.3s ease;
}

.test-button {
  background-color: var(--color-background-soft);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.download-button:hover {
  background-color: #6000CC;
}

.guide-steps {
  margin-top: 40px;
}

.step {
  display: flex;
  margin-bottom: 40px;
  gap: 20px;
}

.step-number {
  width: 40px;
  height: 40px;
  background-color: #7800FF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h3 {
  margin-bottom: 10px;
  color: var(--color-text);
}

.step-content p {
  margin-bottom: 8px;
  color: var(--color-text);
  opacity: 0.8;
  line-height: 1.5;
}

code {
  background-color: var(--code-bg-color);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

.settings-tab {
  padding: 20px;
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.settings-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'RostelecomBasis', sans-serif;
  color: var(--color-text);
}

.settings-button:hover {
  background-color: var(--chat-button-hover);
}

.image-display-select {
  padding: 10px 15px;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  max-width: 250px;
  font-family: 'RostelecomBasis', sans-serif;
  color: var(--color-text);
}

.image-display-select:focus {
  outline: none;
  border-color: #7800FF;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-toggle:hover {
  background-color: var(--chat-button-hover);
}

.tickets-tab {
  padding: 20px;
}

.tickets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.new-ticket-btn {
  padding: 10px 20px;
  background-color: #7800FF;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.new-ticket-btn:hover {
  background-color: #6000CC;
}

.chat-selection {
  max-height: 400px;
  overflow-y: auto;
}

.chat-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
}

.chat-item:hover {
  background-color: var(--chat-button-hover);
}

.tickets-list {
  min-height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-tickets {
  color: var(--color-text);
  opacity: 0.6;
  font-size: 16px;
}

.subscription-tab {
  padding: 20px;
}

.subscription-plans {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
  gap: 15px; 
  margin-top: 15px; 
}


.plan-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 15px; 
  transition: all 0.3s ease;
}

.plan-card.active {
  border-color: #7800FF;
  box-shadow: 0 5px 15px rgba(120, 0, 255, 0.1);
}

.plan-card h3 {
  font-size: 1.2rem; 
  margin-bottom: 8px; 
  color: var(--color-text);
}

.price {
    font-size: 1.4rem; 
    margin-bottom: 10px;
    margin-bottom: 15px;
    color: #7800FF;
}

.features {
  list-style: none;
  padding: 0;
  margin-bottom: 20px;
}

.features li {
  padding: 6px 0;
  font-size: 0.9rem;
  border-bottom: 1px solid var(--color-border-soft);
}

.features li:last-child {
  border-bottom: none;
}

.select-btn {
  width: 100%;
  font-size: 0.9rem;
  padding: 10px;
  background-color: #7800FF;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.select-btn:hover {
  background-color: #6000CC;
}

.select-btn.selected {
  background-color: #e0e0e0;
  color: #666;
  cursor: default;
}

/* Тикеты */
.tickets-list {
  padding: 20px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px;
  color: var(--color-text);
  opacity: 0.7;
}

.spin {
  animation: spin 1s linear infinite;
}

.empty-tickets {
  text-align: center;
  padding: 40px;
  color: var(--color-text);
  opacity: 0.6;
}

.ticket-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tickets-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.sort-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.sort-button:hover {
  background-color: var(--chat-button-hover);
}

@media (max-width: 768px) {
  .tickets-actions {
    flex-direction: column;
    align-items: flex-end;
  }
  
  .sort-button {
    padding: 6px 10px;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Анимации */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-slide-enter-to,
.fade-slide-leave-from {
  opacity: 1;
  transform: translateX(0);
}

@media (max-width: 768px) {
  .Menu {
    flex-direction: column;
    width: 95%;
    max-height: 85vh;
  }
  
  .Menu-sidebar {
    width: 100%;
    padding: 10px 0;
    display: flex;
    overflow-x: auto;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }
  
  .Menu-sidebar button {
    flex-direction: column;
    padding: 10px;
    font-size: 12px;
    gap: 5px;
    min-width: 80px;
  }
  
  .Menu-content {
    padding: 15px;
  }
  
  .profile-avatar {
    width: 80px;
    height: 80px;
  }
  
  .step {
    flex-direction: column;
    gap: 10px;
    margin-bottom: 30px;
  }

  .subscription-plans {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  .plan-card {
    padding: 12px;
  }

  .guide-header h1 {
    font-size: 1.5rem;
  }
  
  .download-button {
    padding: 10px 15px;
    font-size: 0.9rem;
  }
}
</style>