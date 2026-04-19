<template>
  <div class="chat-button-container" @mouseenter="onMouseEnter" @mouseleave="onMouseLeave">
    <button 
      class="chat-button"
      @click="handleClick"
      :disabled="loading"
      :class="{ active: isActive }"
    >
      <span v-if="loading">
        <Icon icon="mdi:loading" class="spin" /> Загрузка...
      </span>
      <span v-else>{{ title }}</span>
    </button>
      
    <div class="menu-button-wrapper" v-show="shouldShowMenu">
      <DropdownMenu 
        :items="menuItems"
        @item-click="handleMenuClick"
        align="right"
        trigger="click"
        v-model:is-open="isMenuOpen"
      >
        <template #trigger>
          <button class="menu-button">
            <Icon icon="mdi:dots-horizontal" width="20" height="20" />
          </button>
        </template>
      </DropdownMenu>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import DropdownMenu from './DropdownMenu.vue'
import { useChatStore } from '@/stores/chat.store'
import { useMenuStore } from '@/stores/menu.store'
import { useTicketStore } from '@/stores/ticket.store'
import { useUIStore } from '@/stores/ui.store'
import api from '@/composables/useApi'

const props = defineProps({
  chatId: Number,
  title: String,
  isActive: Boolean
})

const emit = defineEmits(['chat-selected', 'chat-deleted', 'create-ticket'])

const router = useRouter()
const chatStore = useChatStore()
const menuStore = useMenuStore()
const ticketStore = useTicketStore()
const uiStore = useUIStore()

const loading = ref(false)
const showMenuButton = ref(false)
const isMenuOpen = ref(false)



const menuItems = ref([
  { label: 'Создать тикет', action: 'create-ticket', icon: 'mdi:ticket-outline' }, 
  { label: 'Скачать чат', action: 'download', icon: 'mdi:download-outline' },
  { 
    label: 'Удалить чат',
    action: 'delete',
    icon: 'mdi:delete-outline',
    class: 'danger'
  }
])

const shouldShowMenu = computed(() => {
  return props.isActive || (showMenuButton.value && !isMenuOpen.value)
})

const onMouseEnter = () => {
  if (!props.isActive) {
    showMenuButton.value = true
  }
}

const onMouseLeave = () => {
  if (!props.isActive) {
    showMenuButton.value = false
  }
}

watch(() => props.isActive, (newVal) => {
  if (!newVal) {
    showMenuButton.value = false
    isMenuOpen.value = false
  }
})

const handleClick = async () => {
  loading.value = true
  try {
    const response = await api.getChat(props.chatId)
    
    const messages = Array.isArray(response.data) 
      ? response.data.map(msg => ({
          sender: msg.sender_type === 'user' ? 'user' : 'bot',
          text: msg.content,
          timestamp: msg.date_of_create,
          id: msg.id
        }))
      : []
    
    emit('chat-selected', {
      id: Number(props.chatId), 
      title: props.title,
      messages: messages
    })
  } catch (error) {
    console.error('Ошибка загрузки чата:', error)
    emit('chat-selected', {
      id: Number(props.chatId),
      title: props.title,
      messages: [],
      error: getErrorMessage(error)
    })
  } finally {
    loading.value = false
  }
}

const handleMenuClick = async (item) => {
  if (item.action === 'delete') {
    await deleteChat()
  } else if (item.action === 'download') {
    await downloadChat()
  } else if (item.action === 'create-ticket') {
    await createTicket()
  }
  isMenuOpen.value = false
}

const createTicket = async () => {
  try {
    const success = await ticketStore.openTicketEditor(props.chatId)
    if (success) {
      menuStore.openMenu('tickets')
    }
  } catch (error) {
    console.error('Error creating ticket:', error)
  }
}

const deleteChat = async () => {
  try {
    loading.value = true;
    await api.deleteChat(props.chatId);
    emit('chat-deleted', props.chatId);
    chatStore.handleChatDeleted(props.chatId);
  } catch (error) {
    console.error('Ошибка удаления чата:', error);
  } finally {
    loading.value = false;
  }
};

const downloadChat = async () => {
  try {
    loading.value = true;
    const response = await api.downloadChat(props.chatId);
    
    const messages = response.data || [];
    const chatContent = messages
      .map(msg => {
        const sender = msg.sender_type === 'user' ? 'Вы' : 'Ассистент';
        const date = new Date(msg.date_of_create).toLocaleString();
        return `[${date}] ${sender}: ${msg.content}`;
      })
      .join('\n\n');
    
    const blob = new Blob([chatContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Чат_${props.title}_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Ошибка скачивания чата:', error);

  } finally {
    loading.value = false;
  }
};

function getErrorMessage(error) {
  if (error.response) {
    if (error.response.status === 404) return 'Чат не найден'
    if (error.response.status === 401) return 'Требуется авторизация'
    return 'Ошибка сервера'
  }
  return 'Проблемы с соединением'
}
</script>


<style scoped>
.chat-button-container {
  display: flex;
  align-items: center;
  width: 100%;
  position: relative;
}

.chat-button {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  cursor: pointer;
  text-align: left;
  border: none;
  background-color: transparent;
  transition: background-color 0.2s;
  color: inherit;
}

.menu-button-wrapper {
  position: absolute;
  right: 8px;
}

.menu-button {
  background: none;
  border: none;
  cursor: pointer;
  color: #8b5cf6;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
  width: 32px;
  height: 32px;
}

.menu-button:hover {
  background-color: rgba(139, 92, 246, 0.1);
}

.chat-button:hover {
  background-color: var(--chat-button-hover);
}

.night-mode .chat-button:hover {
  background-color: rgba(90, 103, 124, 0.3);
}

.chat-button:disabled {
  background-color: rgba(238, 238, 238, 0.5);
  cursor: not-allowed;
}

.night-mode .chat-button:disabled {
  background-color: rgba(74, 85, 104, 0.5);
}

/* Для активного чата */
.chat-button.active {
  background-color: var(--chat-button-active);
  font-weight: 500;
}

.night-mode .chat-button.active {
  background-color: rgba(90, 103, 124, 0.5);
}

.spin {
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 6px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>