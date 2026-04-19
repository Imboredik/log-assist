<template>
  <div>
    <div :class="['sidebar', { collapsed: chatStore.isSidebarCollapsed }]" v-show="!chatStore.isSidebarCollapsed">
      <div class="sidebar-header">
        <div class="logo">Log<span class="ai">Assist</span></div>
      </div>
      
      <div class="sidebar-content">
        <div class="section" v-if="chatStore.loadingChats">
          <div class="section-title">Загрузка чатов...</div>
        </div>

        <template v-else>
          <div class="section" v-if="chatStore.todayChats.length > 0">
            <div class="section-title">Сегодня</div>
            <ChatButton
              v-for="chat in chatStore.todayChats"
              :key="Number(chat.id)"
              :chat-id="Number(chat.id)"
              :title="chat.name"
              :is-active="chatStore.activeChatId === Number(chat.id)"
              @chat-selected="handleChatSelected"
              @chat-deleted="handleChatDeleted"
              @create-ticket="handleCreateTicket" 
            />
          </div>

          <div class="section" v-if="chatStore.yesterdayChats.length > 0">
            <div class="section-title">Вчера</div>
            <ChatButton
              v-for="chat in chatStore.yesterdayChats"
              :key="Number(chat.id)"
              :chat-id="Number(chat.id)"
              :title="chat.name"
              :is-active="chatStore.activeChatId === Number(chat.id)"
              @chat-selected="handleChatSelected"
              @chat-deleted="handleChatDeleted"
              @create-ticket="handleCreateTicket" 
            />
          </div>

          <div class="section" v-if="chatStore.earlierChats.length > 0">
            <div class="section-title">Ранее</div>
            <ChatButton
              v-for="chat in chatStore.earlierChats"
              :key="Number(chat.id)"
              :chat-id="Number(chat.id)"
              :title="chat.name"
              :is-active="chatStore.activeChatId === Number(chat.id)"
              @chat-selected="handleChatSelected"
              @chat-deleted="handleChatDeleted"
              @create-ticket="handleCreateTicket" 
            />
          </div>
        </template>
      </div>
    </div>

  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import ChatButton from './ChatButton.vue'
import { useChatStore } from '@/stores/chat.store'
import { useMenuStore } from '@/stores/menu.store'
import { useTicketStore } from '@/stores/ticket.store'

const chatStore = useChatStore()
const menuStore = useMenuStore() 
const ticketStore = useTicketStore()

const handleChatSelected = (chatData) => {
  chatStore.handleChatSelected(chatData)
}

const handleChatDeleted = (deletedChatId) => {
  chatStore.handleChatDeleted(deletedChatId)
}

const emit = defineEmits(['create-ticket']);

const handleCreateTicket = async (chatId) => {
  try {
    const success = await ticketStore.openTicketEditor(chatId)
    if (success) {
      menuStore.openMenu('tickets')
    }
  } catch (error) {
    console.error('Error creating ticket:', error)
  }
}

onMounted(() => {
  chatStore.loadUserChats()
})
</script>

<style scoped>
.sidebar {
  left: 0;
  padding: 0;
  margin: 0;
  width: 280px;
  height: 100vh;
  background-color: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  box-shadow: 2px 0 5px rgba(0,0,0, 0.05);
  left: 0;
  top: 0;
  z-index: 100; 
  overflow-y: auto;
  box-sizing: border-box;
  position: absolute;
  transition: 
    transform 0.3s ease, 
    opacity 0.3s ease,
    width 0.3s ease,
    background-color 0.3s ease;
}

.sidebar.collapsed {
  transform: translateX(-100%);
  opacity: 0;
  width: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.sidebar-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 20px;
  margin-top: 20px;
}

.ai {
  color: #8b5cf6;
  font-size: 22px;
  font-weight: bold;
  margin-top: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@media (max-width: 768px) {
 .sidebar {
    width: 100%;
    position: fixed;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .sidebar-header {
    padding-top: 20px; 
  }

  .sidebar-collapsed-icon {
    display: block;
    position: fixed;
    left: 10px;
    top: 10px;
    z-index: 1100;
    background-color: #FCF9FF;
    padding: 8px;
    border-radius: 50%;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@media (max-width: 768px) {
 .sidebar {
    width: 100%;
    position: fixed;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .sidebar-header {
    padding-top: 20px; 
  }

  .sidebar-collapsed-icon {
    display: block;
    position: fixed;
    left: 10px;
    top: 10px;
    z-index: 1100;
    background-color: #FCF9FF;
    padding: 8px;
    border-radius: 50%;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }
}
</style>