<template>
  <div class="panel">
    <!-- Кнопка переключения sidebar -->
    <button class="toggle-sidebar-btn" @click="chatStore.toggleSidebar">
      <Icon 
        :icon="chatStore.isSidebarCollapsed ? 'mynaui:panel-left-open' : 'mynaui:panel-left-close'" 
        width="24" 
        height="24" 
      />
    </button>
    <!-- Панель пользователя с выпадающим меню -->
    <div class="user-info">
      <DropdownMenu :items="userMenuItems" 
        @item-click="handleMenuClick"
        trigger="click"
        align="right"
      >
        <template #trigger>
          <div class="user-trigger">
            <div class="user-data">
              <div class="user-name">{{ authStore.user?.username || 'Пользователь' }}</div>
              <div class="user-status">{{ authStore.user?.role || 'Пользователь' }}</div>
            </div>
            <div 
              class="avatar"
              :style="{ 
                backgroundImage: authStore.user?.avatarUrl ? `url(${authStore.user.avatarUrl})` : 'none',
                backgroundColor: !authStore.user?.avatarUrl ? '#ddd' : 'transparent'
              }"
            ></div>
          </div>
        </template>
      </DropdownMenu>
    </div>

    <!-- Меню личного кабинета -->
    <Menu @close="menuStore.closeMenu" />
  </div>
</template>

<script setup>
import { Icon } from '@iconify/vue'
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import DropdownMenu from './DropdownMenu.vue'
import Menu from './Menu.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useUIStore } from '@/stores/ui.store'
import { useChatStore } from '@/stores/chat.store'
import { useMenuStore } from '@/stores/menu.store'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()
const chatStore = useChatStore()
const menuStore = useMenuStore()

const userMenuItems = ref([
  { label: 'Личный кабинет', action: 'account', icon: 'mdi:account-outline' },
  { 
    label: authStore.user?.subscription === 'free' ? 'Оформить подписку' : 'Сменить тариф', 
    action: 'subscription', 
    icon: 'streamline-flex:subscription-cashflow' 
  },
  { 
    label: uiStore.isNightMode ? 'Дневной режим' : 'Ночной режим', 
    action: 'night-mode', 
    icon: uiStore.isNightMode ? 'mdi:weather-sunny' : 'mdi:weather-night' 
  },
  { 
    label: 'Выйти', 
    action: 'logout', 
    icon: 'mdi:logout-variant',
    class: 'danger'
  }
])

const handleMenuClick = async (item) => {
  if (item.action === 'night-mode') {
    uiStore.toggleNightMode()
    userMenuItems.value = userMenuItems.value.map(menuItem => {
      if (menuItem.action === 'night-mode') {
        return {
          ...menuItem,
          label: uiStore.isNightMode ? 'Дневной режим' : 'Ночной режим',
          icon: uiStore.isNightMode ? 'mdi:weather-sunny' : 'mdi:weather-night'
        }
      }
      return menuItem
    })
  } else if (item.action === 'logout') {
    await logout()
  } else if (item.action === 'account') {
    menuStore.openMenu('profile')
  } else if (item.action === 'subscription') {
    menuStore.openMenu('subscription')
  }
}

const logout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Ошибка при выходе:', error)
  }
}

watch(() => authStore.user?.subscription, (newSubscription) => {
  userMenuItems.value = userMenuItems.value.map(item => {
    if (item.action === 'subscription') {
      return {
        ...item,
        label: newSubscription === 'free' ? 'Оформить подписку' : 'Сменить тариф'
      }
    }
    return item
  })
}, { immediate: true })

</script>

<style scoped>
.panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
  padding: 0 20px;
  background-color: var(--panel-bg);
  border-bottom-color: var(--panel-border);
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  width: 100%;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.toggle-sidebar-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #D8D8D8;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  transition: transform 0.4s cubic-bezier(0.68, -0.6, 0.32, 1.6);
}

.toggle-sidebar-btn:hover {
  color: #7800FF;
  transform: scale(1.05); 
}

.menu-button {
  font-family: 'RostelecomBasis', sans-serif;
  font-weight: 400;
  background: none;
  border: none;
  font-size: 30px;
  cursor: pointer;
  color: #999;
  padding: 5px 10px;
}

.user-info {
  position: relative;
  margin-left: auto; 
  max-width: 100%;
  margin-right: 80px;
}

.user-trigger {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 6px;
  max-width: 100%;
  overflow: hidden;
  gap: 12px;
  transition: background-color 0.3s ease;
  cursor: pointer; 
}

.user-trigger:hover {
  background-color: #CFABF9;
}

.user-data {
  display: flex;
  flex-direction: column;
  margin-right: 8px;
  text-align: right;
  max-width: 200px; 
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-name {
  font-family: 'RostelecomBasis', sans-serif;
  font-weight: 500;
  margin-bottom: 2px;
  font-size: 14px; 
  margin-bottom: 2px;
}

.user-status {
  font-family: 'RostelecomBasis', sans-serif;
  font-weight: 500;
  font-size: 12px;
  color: gray;
}

.avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background-color: #ddd;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* Ночной режим */ 
.night-mode .user-trigger:hover {
  background-color: #2d3748; 
}

/* Мобильная версия */ 
@media (max-width: 768px) {
  .panel {
    padding: 0 10px;
    height: 60px;
  }

  .user-info {
    margin-right: 10px;
  }

  .avatar {
    width: 35px;
    height: 35px;
  }

  .user-name {
    max-width: 120px;
  }
  
  .user-status {
    max-width: 120px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>