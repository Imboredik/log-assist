<!-- Chat.vue -->
<template>
  <div class="chat-container">
    <ImagePreview ref="imagePreview" :images="previewImages" />
    
    <div class="chat-body" ref="chatBody">
      <MessageBubble
        v-for="(msg, index) in chatStore.activeChatMessages"
        :key="index"
        :sender="msg.sender"
        :text="msg.text"
        :images="msg.images"
        :typing="msg.typing"
        :timestamp="msg.timestamp"
        :is-typing-complete="msg.isTypingComplete"
        :is-first-bot-message="isFirstBotMessage(msg)"
        :is-action-loading="isActionLoading"
        :image-display-mode="imageDisplayMode"
        @open-image-preview="openImagePreview"
        @analysis="handleAnalysis"
        @solution="handleSolution"
        @create-ticket="handleCreateTicket"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted, onMounted } from 'vue'
import FileAttachment from './FileAttachment.vue'
import { useChatStore } from '@/stores/chat.store'
import { useTicketStore } from '@/stores/ticket.store'
import { useMenuStore } from '@/stores/menu.store'
import ImagePreview from './ImagePreview.vue'
import MessageBubble from './MessageBubble.vue'
import api from '@/composables/useApi'

const chatStore = useChatStore()
const ticketStore = useTicketStore()
const menuStore = useMenuStore()
const chatBody = ref(null)
const abortController = ref(null)
const isActionLoading = ref(false)
const imagePreview = ref(null)
const previewImages = ref([])
const ai = 'ai'
const imageDisplayMode = ref('image')

const stopTyping = () => {
  if (abortController.value) {
    abortController.value.abort()
  }
}

onMounted(() => {
  const savedMode = localStorage.getItem('imageDisplayMode')
  if (savedMode) {
    imageDisplayMode.value = savedMode
  }
})

defineExpose({
  stopTyping
})

const isFirstBotMessage = (msg) => {
  const msgIndex = chatStore.activeChatMessages.findIndex(m => m.id === msg.id);
  return msg.sender === ai && msgIndex === 1;
}

const openImagePreview = (images, index) => {
  previewImages.value = images
  nextTick(() => {
    imagePreview.value.open(index)
  })
}

const handleAnalysis = async () => {
  if (isActionLoading.value || !chatStore.activeChatId) return
  
  try {
    isActionLoading.value = true
    const botMessage = {
      id: Date.now(),
      sender: ai,
      text: '',
      typing: true,
      timestamp: new Date().toISOString(),
      isTypingComplete: false
    }
    chatStore.insertMessageInOrder(botMessage)
    
    const response = await api.getAnalysis(chatStore.activeChatId)
    if (response?.data?.content) {
      await chatStore.typeMessage(botMessage.id, response.data.content)
    }
  } catch (error) {
    console.error('Analysis error:', error)
    const errorMessage = {
      sender: ai,
      text: 'Произошла ошибка при выполнении анализа. Пожалуйста, попробуйте позже.',
      timestamp: new Date().toISOString(),
      isTypingComplete: true
    }
    chatStore.insertMessageInOrder(errorMessage)
  } finally {
    isActionLoading.value = false
  }
}

const handleSolution = async () => {
  if (isActionLoading.value || !chatStore.activeChatId) return
  
  try {
    isActionLoading.value = true
    const botMessage = {
      id: Date.now(),
      sender: ai,
      text: '',
      typing: true,
      timestamp: new Date().toISOString(),
      isTypingComplete: false
    }
    chatStore.insertMessageInOrder(botMessage)
    
    const response = await api.getSolution(chatStore.activeChatId)
    if (response?.data?.content) {
      await chatStore.typeMessage(botMessage.id, response.data.content)
    }
  } catch (error) {
    console.error('Solution error:', error)
    const errorMessage = {
      sender: ai,
      text: 'Произошла ошибка при поиске решения. Пожалуйста, попробуйте позже.',
      timestamp: new Date().toISOString(),
      isTypingComplete: true
    }
    chatStore.insertMessageInOrder(errorMessage)
  } finally {
    isActionLoading.value = false
  }
}

const handleCreateTicket = async () => {
  try {
    const success = await ticketStore.openTicketEditor(chatStore.activeChatId)
    if (success) {
      menuStore.openMenu('tickets')
    }
  } catch (error) {
    console.error('Error creating ticket:', error)
  }
}

onUnmounted(() => {
  stopTyping() // Now we can safely call it here
})

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBody.value) {
      try {
        chatBody.value.scrollTop = chatBody.value.scrollHeight
      } catch (error) {
        console.error('Scroll error:', error)
      }
    }
  })
}

const handleMessagesChange = (newMessages, oldMessages) => {
  try {
    const shouldScroll = newMessages.some(msg => 
      (msg.sender === 'user' && (!oldMessages || !oldMessages.some(m => m.id === msg.id))) ||
      (msg.sender === ai && msg.isTypingComplete && 
       (!oldMessages || !oldMessages.some(m => m.id === msg.id && m.isTypingComplete))))
    
    if (shouldScroll) {
      scrollToBottom();
    }
  } catch (error) {
    console.error('Error in messages watcher:', error);
  }
};

watch(() => [...chatStore.activeChatMessages], handleMessagesChange, { 
  deep: true, 
  immediate: true,
  flush: 'post' 
});
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  padding-top: 70px;
  height: calc(100% - 70px);
  background-color: transparent !important;
}

.chat-body {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 70px;
  left: 0;
  width: calc(100% - 8px);
  overflow-y: scroll;
  padding: 16px 20px 20px 16px;
  scrollbar-gutter: stable;
  display: flex;
  flex-direction: column;
  background-color: transparent !important;
  gap: 6px;
}

/* Night mode */
.night-mode .chat-container {
  background-color: var(--color-background);
}

.night-mode .chat-body {
  background-color: var(--color-background);
}

@media (max-width: 768px) {
  .chat-container {
    padding-top: 10px;
    height: calc(100vh - 120px);
  }
}
</style>