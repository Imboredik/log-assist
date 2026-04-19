<template>
  <router-view />
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.store'
import { useUIStore } from '@/stores/ui.store'
import { useChatStore } from '@/stores/chat.store'
import { useRouter } from 'vue-router'
import { onMounted, onUnmounted } from 'vue'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()
const chatStore = useChatStore()

const handleSystemThemeChange = (e) => {
  if (localStorage.getItem('nightMode') === null) {
    uiStore.isNightMode = e.matches
    uiStore.applyTheme()
  }
}

onMounted(async () => {
  uiStore.initializeTheme()
  
  const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  darkModeMediaQuery.addEventListener('change', handleSystemThemeChange)

  const urlParams = new URLSearchParams(window.location.search)
  const tokenFromUrl = urlParams.get('token')
  const chatIdFromUrl = urlParams.get('chat_id')
  const isExtensionRequest = urlParams.get('extension') === 'true'
  
  if (tokenFromUrl) {
    localStorage.setItem('assist-log-token', tokenFromUrl)
    if (typeof chrome !== 'undefined' && chrome.storage) {
      try {
        await chrome.storage.local.set({ 'assist-log-token': tokenFromUrl })
      } catch (e) {
        console.error("Error saving token to chrome.storage:", e)
      }
    }
    
    if (isExtensionRequest) {
      await new Promise(resolve => setTimeout(resolve, 500))
      window.close()
    } else {
      const redirectPath = chatIdFromUrl ? `/chat?chat_id=${chatIdFromUrl}` : '/chat'
      router.push(redirectPath)
    }
    
    window.history.replaceState({}, document.title, window.location.pathname)
  }

  if (chatIdFromUrl) {
    if (!tokenFromUrl) {
      authStore.setPendingChatId(chatIdFromUrl)
    } else {
      // Если токен есть, сразу загружаем чат
      chatStore.loadChat(chatIdFromUrl)
    }
  }

  try {
    await authStore.checkAuth()
    
    if (authStore.pendingChatId) {
      const pendingId = authStore.pendingChatId
      authStore.setPendingChatId(null)
      chatStore.loadChat(pendingId)
    }
  } catch (error) {
    console.error('Auth check error:', error)
  }
})

onUnmounted(() => {
  window.matchMedia('(prefers-color-scheme: dark)')
    .removeEventListener('change', handleSystemThemeChange)
})
</script>

<style>
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  color: var(--color-text);
  background-color: var(--color-background);
  transition: background-color 0.3s ease, color 0.3s ease;
}

#app {
  height: 100%;
  background-color: var(--color-background);
  color: var(--color-text);
  transition: background-color 0.3s ease, color 0.3s ease;
}
</style>