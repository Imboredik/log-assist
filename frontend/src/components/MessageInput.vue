<template>
  <div :class="$style['input-wrapper']">
    <ImagePreview 
      v-if="images.length > 0"
      :images="images"
      @remove-image="removeImage"
    />
    <div :class="$style['input-container']">
      <textarea
        v-model="chatStore.messageInput"
        ref="input"
        :class="$style['message-input']"
        placeholder="Введите сообщение…"
        @input="autoResize"
        @keyup.enter.exact="handleSend"
        @paste="handlePaste"
        rows="1"
        :disabled="chatStore.isSending || chatStore.isBotTyping"
      />
      <div :class="$style['button-group']">
        <button 
          :class="$style['attach-button']"
          @click="triggerFileInput"
        >
          <Icon icon="mdi:paperclip" width="20" height="20" />
        </button>
        <button 
          :class="$style['send-button']" 
          @click="handleSend"
          :disabled="chatStore.isSending || (!chatStore.isBotTyping && !(chatStore.messageInput || '').trim() && images.length === 0)" 
        >
          <Icon 
            :icon="chatStore.isBotTyping ? 'mdi:square' : (chatStore.isSending ? 'svg-spinners:270-ring' : 'mdi:arrow-up')" 
            width="18" 
            height="18" 
            color="white" 
          />
        </button>
      </div>
      <input
        type="file"
        ref="fileInput"
        :class="$style['file-input']"
        accept="image/*"
        @change="handleFileSelect"
        multiple
      />
    </div>
    
    <!-- Уведомление о слишком большом файле -->
    <transition name="fade">
      <div v-if="showSizeError" :class="$style['size-error']">
        Файл слишком большой (макс. {{ MAX_IMAGE_SIZE / 1024 / 1024 }}MB)
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { useChatStore } from '@/stores/chat.store'
import ImagePreview from './ImageMiniPreview.vue'

const MAX_IMAGE_COUNT = 2
const MAX_IMAGE_SIZE = 2 * 1024 * 1024 // 2MB в байтах

const chatStore = useChatStore()
const input = ref(null)
const fileInput = ref(null)
const images = ref([])
const showSizeError = ref(false)

const autoResize = () => {
  if (input.value) {
    input.value.style.height = 'auto'
    input.value.style.height = input.value.scrollHeight + 'px'
  }
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  if (files.length === 0) return
  
  // Проверяем общее количество изображений
  const remainingSlots = MAX_IMAGE_COUNT - images.value.length
  if (remainingSlots <= 0) {
    alert(`Максимальное количество изображений: ${MAX_IMAGE_COUNT}`)
    return
  }
  
  // Берем только первые N файлов, чтобы не превысить лимит
  const filesToAdd = files.slice(0, remainingSlots)
  
  for (const file of filesToAdd) {
    if (file.type.startsWith('image/')) {
      // Проверяем размер файла
      if (file.size > MAX_IMAGE_SIZE) {
        showSizeError.value = true
        setTimeout(() => showSizeError.value = false, 3000)
        continue
      }
      
      const reader = new FileReader()
      reader.onload = (event) => {
        images.value.push({
          url: event.target.result,
          file: file
        })
      }
      reader.readAsDataURL(file)
    }
  }
  
  // Reset file input
  e.target.value = ''
}

const handlePaste = (e) => {
  const items = (e.clipboardData || window.clipboardData).items
  if (!items) return
  
  // Проверяем лимит изображений
  if (images.value.length >= MAX_IMAGE_COUNT) {
    alert(`Максимальное количество изображений: ${MAX_IMAGE_COUNT}`)
    return
  }
  
  for (let i = 0; i < items.length; i++) {
    if (items[i].type.startsWith('image/')) {
      const blob = items[i].getAsFile()
      
      // Проверяем размер файла
      if (blob.size > MAX_IMAGE_SIZE) {
        showSizeError.value = true
        setTimeout(() => showSizeError.value = false, 3000)
        e.preventDefault()
        return
      }
      
      const reader = new FileReader()
      reader.onload = (event) => {
        images.value.push({
          url: event.target.result,
          file: blob
        })
      }
      reader.readAsDataURL(blob)
      e.preventDefault()
      break // Добавляем только одно изображение из буфера обмена
    }
  }
}

const removeImage = (index) => {
  images.value.splice(index, 1)
}

const handleSend = async () => {
  const messageToSend = chatStore.messageInput?.trim() || '';

  if (!messageToSend && images.value.length === 0) return;

  try {
    await chatStore.sendMessage({
      text: messageToSend,
      chatId: chatStore.activeChatId,
      localImages: images.value
    });

    // Сброс высоты textarea
    if (input.value) {
      input.value.style.height = 'auto';
    }
  } catch (error) {
    console.error('Error sending message:', error);
  }
}

watch(() => chatStore.messageInput, autoResize)

onMounted(() => {
  autoResize()
  input.value?.focus()
})
</script>

<style module>
.input-wrapper {
  position: relative;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto 16px;
}

.input-container {
  width: 100%; 
  height: 100%;
  display: flex;
  align-items: flex-end;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 24px;
  background-color: var(--input-bg);
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
  max-height: 300px;
  transition: all 0.3s ease;
  position: relative;
}

.input-container:focus-within {
  border-color: #CFABF9;
  box-shadow: 0 0 0 2px rgba(218, 191, 255, 0.2);
}

.button-group {
  display: flex;
  align-items: center;
  margin-left: 8px;
  gap: 4px;
}

.attach-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: var(--color-text);
  opacity: 0.7;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.attach-button:hover {
  opacity: 1;
}

.file-input {
  display: none;
}

.message-input {
  flex: 1;
  resize: none;
  overflow-y: auto;
  line-height: 1.5em;
  font-size: 15px;
  padding: 8px 12px;
  border: none;
  outline: none;
  background-color: transparent;
  font-family: inherit;
  color: var(--color-text);
  min-height: 80px;
  max-height: 280px; 
  box-sizing: border-box; 
  transition: all 0.3s ease;
  overflow-y: auto; 
  margin-right: 8px;
}

.message-input:disabled {
  cursor: not-allowed;
  background-color: transparent;
}

.message-input::placeholder {
  color: var(--color-text);
}

.send-button {
  background-color: #CFABF9;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  min-width: 32px;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: 8px;
}

.send-button:hover:not(:disabled) {
  background-color: #7800FF;
  transform: scale(1.05);
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--color-background-mute);
}

/* Стили для уведомления о размере */
.size-error {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background-color: #ff4444;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Стили для ночного режима */
.night-mode .input-container {
  background-color: var(--color-background-soft);
  border-color: var(--color-border);
}

.night-mode .message-input {
  color: var(--color-text);
}

.night-mode .message-input::placeholder {
  color: var(--vt-c-text-dark-2);
}

.night-mode .send-button {
  background-color: #6b46c1;
}

.night-mode .send-button:hover:not(:disabled) {
  background-color: #805ad5;
}

.night-mode .send-button:disabled {
  background-color: var(--color-background-mute);
}

.night-mode .attach-button {
  color: var(--color-text);
}

@media (max-width: 768px) {
  .input-wrapper {
    width: 90%;
  }
}
</style>