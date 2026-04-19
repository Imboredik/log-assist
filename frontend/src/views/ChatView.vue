<template>
  <div class="container" :class="{ 
      'is-sidebar-collapsed': chatStore.isSidebarCollapsed,
      'night-mode': uiStore.isNightMode 
    }" :style="{ 
      backgroundColor: uiStore.isNightMode ? 'var(--color-background)' : '' 
    }">
    <Sidebar />
    <div class="mainContent" :style="{ marginLeft: chatStore.isSidebarCollapsed ? '0' : '280px' }">
      <Panel />
      <div class="chat-content">
        <div v-if="chatStore.activeChatId === null" class="no-chat-selected">
          <div class="no-chat-message">
            Выберите чат из списка слева или создайте новый
          </div>
        </div>
        
        <template v-else>
          <div v-if="chatStore.isLoadingMessages" class="loading-messages">
            Загрузка сообщений...
          </div>
          <template v-else>
            <Chat />
            <div class="input-fixed">
              <MessageInput />
            </div>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>


<script setup>

import Sidebar from '../components/Sidebar.vue'
import Panel from '../components/Panel.vue'
import Chat from '../components/Chat.vue'
import MessageInput from '../components/MessageInput.vue'
import { useChatStore } from '@/stores/chat.store'
import { useUIStore } from '@/stores/ui.store'

const chatStore = useChatStore()
const uiStore = useUIStore()
</script>


<style scoped>
.container {
  font-family: 'RostelecomBasis', sans-serif;
  display: flex;
  width: 100vw;
  min-width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: var(--color-background);
  color: var(--color-text);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.mainContent {
  position: relative;
  padding: 0;
  margin: 0;
  flex: 1;
  width: calc(100% - 280px);
  height: 100vh;
  margin-left: 280px;
  transition: margin-left 0.3s ease, width 0.3s ease;
  display: flex;
  flex-direction: column;
  font-family: 'RostelecomBasis', sans-serif;
  background-color: var(--color-background);
}

.is-sidebar-collapsed .mainContent {
  margin-left: 0 !important; 
  width: 100% !important;
}

.is-sidebar-collapsed .input-fixed {
  left: 0; 
}

.header-panel {
  position: sticky;
  top: 0;
  z-index: 1000; 
}

.content-wrapper {
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 70px); 
  flex: 1;
  position: relative;
  overflow: hidden;
}

.chat-content {
  max-width: 800px;
  margin: 0 auto;
  flex: 1;
  overflow-y: auto;

  padding-top: 10px;
  overflow: hidden;
  margin: 0 auto; 
  width: 100%;
  position: relative;
  z-index: 10;
}

.input-fixed {
  position: fixed;
  bottom: 0;
  left: 280px;
  right: 0;
  width: calc(100% - 280px);
  max-width: 800px;
  margin: 0 auto;
  padding: 16px 0; 
  background: transparent; 
  z-index: 100;
  transition: all 0.3s ease;
  box-sizing: border-box;
}


.content > :first-child {
  flex: 1;
  overflow-y: auto;
  min-height: 0; 
}

.content > :last-child {
  flex-shrink: 0;
}

.no-chat-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--color-text);
  font-size: 18px;
  text-align: center;
  padding: 20px;
}

.no-chat-message {
  background: var(--color-background-soft); 
  padding: 20px 30px;
  border-radius: 10px;
  max-width: 80%;
  color: var(--color-text); 
  border: 1px solid var(--color-border); 
}

.loading-messages {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
  font-size: 18px;
  padding: 20px;
}

.loading-messages::after {
  content: "...";
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%, 20% { content: "."; }
  40% { content: ".."; }
  60%, 100% { content: "..."; }
}



/* Мобильные стили */

@media (max-width: 768px) {
  .mainContent {
    margin-left: 0 !important;
    width: 100% !important;
  }
  
  .input-fixed {
    left: 0 !important;
    width: 100% !important;
  }
  
  .sidebar {
    position: fixed;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
}

</style>