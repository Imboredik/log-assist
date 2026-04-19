<template>
  <div class="chat-selection">
    <div class="header">
      <h2>Выберите чат для создания тикета</h2>
      <button class="close-btn" @click="close">
        <Icon icon="mdi:close" width="24" height="24" />
      </button>
    </div>
    
    <div class="chat-list">
      <div v-if="chatStore.loadingChats" class="loading">Загрузка чатов...</div>
      
      <template v-else>
        <div class="section" v-if="chatStore.todayChats.length > 0">
          <div class="section-title">Сегодня</div>
          <div 
            v-for="chat in chatStore.todayChats"
            :key="chat.id"
            class="chat-item"
            @click="selectChat(chat.id)"
          >
            {{ chat.name }}
          </div>
        </div>

        <div class="section" v-if="chatStore.yesterdayChats.length > 0">
          <div class="section-title">Вчера</div>
          <div 
            v-for="chat in chatStore.yesterdayChats"
            :key="chat.id"
            class="chat-item"
            @click="selectChat(chat.id)"
          >
            {{ chat.name }}
          </div>
        </div>

        <div class="section" v-if="chatStore.earlierChats.length > 0">
          <div class="section-title">Ранее</div>
          <div 
            v-for="chat in chatStore.earlierChats"
            :key="chat.id"
            class="chat-item"
            @click="selectChat(chat.id)"
          >
            {{ chat.name }}
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { useChatStore } from '@/stores/chat.store'
import { useTicketStore } from '@/stores/ticket.store'
import { Icon } from '@iconify/vue'

const chatStore = useChatStore()
const ticketStore = useTicketStore()

const selectChat = async (chatId) => {
  await ticketStore.openTicketEditor(chatId)
}

const close = () => {
  ticketStore.isChatSelectionOpen = false
}
</script>

<style scoped>
.chat-selection {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text);
  opacity: 0.7;
}

.close-btn:hover {
  opacity: 1;
}

.chat-list {
  max-height: 400px;
  overflow-y: auto;
}

.section {
  margin-bottom: 20px;
}

.section-title {
  font-weight: 500;
  margin-bottom: 10px;
  color: var(--color-text);
  opacity: 0.8;
}

.chat-item {
  padding: 12px;
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 5px;
  background-color: var(--color-background-soft);
  transition: background-color 0.2s;
}

.chat-item:hover {
  background-color: var(--chat-button-hover);
}

.loading {
  padding: 20px;
  text-align: center;
  color: var(--color-text);
  opacity: 0.7;
}
</style>