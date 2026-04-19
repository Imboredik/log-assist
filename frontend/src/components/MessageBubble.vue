<template>
  <div :class="['message-bubble', sender === 'user' ? 'user-message' : 'bot-message']">
    <!-- Images -->
    <div v-if="images && images.length > 0" class="message-attachments">
      <template v-if="imageDisplayMode === 'image'">
        <div class="images-grid" :class="`grid-${Math.min(images.length, 4)}`">
          <img 
            v-for="(img, imgIndex) in images" 
            :key="imgIndex" 
            :src="img" 
            class="message-image"
            @click="$emit('open-image-preview', images, imgIndex)"
          />
        </div>
      </template>
      <template v-else>
        <div class="file-attachments-grid">
          <FileAttachment 
            v-for="(img, imgIndex) in images"
            :key="imgIndex"
            :file="{ name: `image_${imgIndex + 1}.jpg`, url: img }"
            @click="$emit('open-image-preview', images, imgIndex)"
          />
        </div>
      </template>
    </div>
    
    <!-- Message text -->
    <div class="message-content markdown" v-if="text" v-html="renderMarkdown(text.trim())"></div>
    
    <span v-if="typing" class="typing-indicator">...</span>
    <span v-if="timestamp" class="message-time">
      {{ formatTime(timestamp) }}
    </span>
    
    <!-- Action buttons for first bot message -->
    <div 
      v-if="isFirstBotMessage && isTypingComplete" 
      class="action-buttons"
    >
      <button 
        @click="$emit('analysis')" 
        :disabled="isActionLoading"
        class="action-button analysis-button"
      >
        Подробный анализ
      </button>
      <button 
        @click="$emit('solution')" 
        :disabled="isActionLoading"
        class="action-button solution-button"
      >
        Решение проблемы
      </button>
    </div>
    
    <!-- Copy and Ticket buttons for bot messages -->
    <div v-if="sender === 'ai' && isTypingComplete" class="message-actions">
      <button 
        class="action-icon copy-button"
        @click="copyMessage"
        :title="isCopied ? 'Скопировано!' : 'Копировать'"
      >
        <Icon :icon="isCopied ? 'mdi:check' : 'mdi:content-copy'" width="16" />
      </button>
      <button 
        class="action-icon ticket-button"
        @click="$emit('create-ticket')"
        title="Создать тикет"
      >
        <Icon icon="mdi:ticket-outline" width="16" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import 'highlight.js/styles/github-dark.css'
import { Icon } from '@iconify/vue'
import FileAttachment from './FileAttachment.vue'

const props = defineProps({
  sender: {
    type: String,
    required: true,
    validator: value => ['user', 'ai'].includes(value)
  },
  text: String,
  images: Array,
  typing: Boolean,
  timestamp: String,
  isTypingComplete: Boolean,
  isFirstBotMessage: Boolean,
  isActionLoading: Boolean,
  imageDisplayMode: {
    type: String,
    default: 'image',
    validator: value => ['image', 'file'].includes(value)
  }
})

const emit = defineEmits([
  'open-image-preview',
  'analysis',
  'solution',
  'create-ticket'
])

const isCopied = ref(false)

const renderer = new marked.Renderer()

renderer.paragraph = (text) => {
  return text; 
}
renderer.text = (text) => {
  return text;
}

marked.setOptions({
  renderer,
  breaks: false,
  gfm: true,
  headerIds: false,
  mangle: false,
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (e) {
        console.error('Error highlighting code:', e);
      }
    }
    return hljs.highlightAuto(code).value;
  },
  renderer: new marked.Renderer({
    heading(text, level) {
      return `<h${level}>${text}</h${level}>`;
    }
  })
})

const preprocessMarkdown = (text) => {
  if (!text) return '';
  return text
    .replace(/\n{3,}/g, '\n\n')
    .replace(/(\r?\n){2,}$/, '\n') 
    .trim();
};

const renderMarkdown = (text) => {
  if (!text) return '';
  const preprocessed = preprocessMarkdown(text);
  const dirty = marked.parse(preprocessed);
  return DOMPurify.sanitize(dirty);
}

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const now = new Date();
  
  if (isNaN(date.getTime())) return '';
  
  const timeStr = date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });
  
  if (date.toDateString() !== now.toDateString()) {
    let dateStr = date.toLocaleDateString([], { day: 'numeric', month: 'numeric' });
    
    if (date.getFullYear() !== now.getFullYear()) {
      dateStr += ` ${date.getFullYear()}`;
    }
    
    return `${dateStr}, ${timeStr}`;
  }
  
  return timeStr;
};

const copyMessage = async () => {
  try {
    const textToCopy = props.text
      .replace(/<[^>]*>/g, '') // Remove HTML tags
      .replace(/\n{3,}/g, '\n\n') // Normalize newlines
      .trim()
    
    await navigator.clipboard.writeText(textToCopy)
    isCopied.value = true
    setTimeout(() => {
      isCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy text: ', err)
  }
}
</script>

<style scoped>
.message-bubble {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: calc(800px - 40px);
  word-break: break-word;
  white-space: normal;
  margin-bottom: 4px;
  padding: 0;
  width: 100%;
  line-height: 1.2;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.message-content {
  max-width: 100%;
  width: fit-content;
  overflow-wrap: break-word;
  word-break: break-word;
  white-space: pre-wrap;
  line-height: 1.4;
  min-width: 40px;
  margin-bottom: 2px;
}

.message-content:only-child {
  min-width: 60px;
}

.user-message {
  align-self: flex-end;
  background-color: var(--message-user-bg);
  color: var(--message-user-text);
  border-radius: 16px;
  border-bottom-right-radius: 6px;
  padding: 8px 12px;
  margin: 2px 0;
  max-width: 80%;
  min-width: min-content;
  width: fit-content;
}

.bot-message {
  align-self: flex-start;
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
  background-color: var(--message-bot-bg);
  color: var(--message-bot-text);
  border-radius: 16px;
  margin-left: 16px;
  padding: 8px 12px;
  margin: 2px 0;
  max-width: 80%;
  min-width: min-content;
  width: fit-content;
}

.message-content.markdown {
  width: 100%;
  padding: 0;
}

.message-content.markdown * {
  margin: 0;
  padding: 0;
  line-height: inherit;
}

.message-content :deep(h1) {
  font-size: 1.5em;
  font-weight: 700;
  margin: 0.25em 0 !important;
}

.message-content :deep(h2) {
  font-size: 1.3em;
  font-weight: 600;
  margin: 0.25em 0 !important;
}

.message-content :deep(h3) {
  font-size: 1.1em;
  font-weight: 500;
  margin: 0.25em 0 !important;
}

.message-content :deep(h4) {
  font-size: 1em;
  font-weight: 500;
  margin: 0.25em 0 !important;
}

.message-content :deep(p) {
  margin: 0.25em 0 !important;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 0.25em 0 !important;
  padding-left: 20px !important;
}

.message-content :deep(li) {
  margin: 0.15em 0 !important;
}

.message-content :deep(pre) {
  background-color: var(--code-bg-color, #f6f8fa);
  border-radius: 6px;
  margin: 0.5em 0 !important;
  padding: 12px 16px !important;
  width: 100%;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-content :deep(code) {
  font-family: 'Courier New', Courier, monospace;
  background-color: transparent;
  padding: 0 !important;
  margin: 0 !important;
  white-space: pre-wrap;
}

.message-content :deep(pre code) {
  display: block;
  background: transparent;
  padding: 0 !important;
}

.message-content :deep(p code),
.message-content :deep(li code) {
  background-color: #f0f0f0;
  padding: 2px 4px !important;
  border-radius: 3px;
  font-size: 0.9em;
}

.message-content :deep(blockquote) {
  border-left: 3px solid #ddd;
  padding-left: 10px;
  margin: 0.5em 0 !important;
  color: #777;
}

.message-content :deep(hr) {
  border: none;
  border-top: 1px solid #ddd;
  margin: 0.75em 0 !important;
}

.message-attachments {
  margin-bottom: 8px;
  width: 100%;
}

.file-attachments-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  width: 100%;
}

.images-grid {
  display: grid;
  gap: 8px;
  width: 100%;
}

.grid-1 {
  grid-template-columns: 1fr;
}

.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-3 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-3 .message-image:first-child {
  grid-column: span 2;
}

.grid-4 {
  grid-template-columns: repeat(2, 1fr);
}

.message-image {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.message-image:hover {
  transform: scale(1.02);
}

.user-message .message-image {
  border-radius: 12px 12px 0 12px;
}

.bot-message .message-image {
  border-radius: 12px 12px 12px 0;
}

.file-attachments {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}


.typing-indicator {
  display: inline-block;
  animation: blink 1.4s infinite;
  font-size: 14px;
  margin-left: 8px;
  color: var(--color-text);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.message-content.markdown {
  transition: opacity 0.2s ease;
}

.bot-message:not(.complete) .message-content {
  opacity: 0.8;
}

.message-content.markdown {
  transition: opacity 0.3s ease;
}

.message-content.markdown:not(.complete) {
  opacity: 0.9;
}

.message-time {
  font-size: 11px;
  color: #aaa;
  margin-top: 0;
  align-self: flex-end;
  line-height: 1.2;
  white-space: nowrap;
}

.message-images {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
  width: 100%;
}

.message-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
  align-self: flex-start;
}

.user-message .message-image {
  align-self: flex-end;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  width: 100%;
  justify-content: flex-start;
}

.action-button {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.analysis-button {
  background-color: #4f46e5;
  color: white;
}

.analysis-button:hover:not(:disabled) {
  background-color: #4338ca;
}

.solution-button {
  background-color: #10b981;
  color: white;
}

.solution-button:hover:not(:disabled) {
  background-color: #0d9f6e;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px; 
  margin-bottom: 12px;
  width: 100%;
  justify-content: flex-start;
}

.action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background-color: rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
  color: inherit;
}

.action-icon:hover {
  background-color: rgba(0, 0, 0, 0.2);
}

.copy-button:hover {
  color: #4f46e5;
}

.ticket-button:hover {
  color: #10b981;
}

/* Night mode styles */
.night-mode .bot-message {
  background-color: transparent;
  color: var(--text-color);
}

.night-mode .message-time {
  color: rgba(255, 255, 255, 0.5);
}

.night-mode .message-content :deep(pre),
.night-mode .message-content :deep(code) {
  background-color: rgba(45, 55, 72, 0.7);
}

.night-mode .message-content :deep(blockquote) {
  border-left-color: #4a5568;
  color: #a0aec0;
}

.night-mode .message-content :deep(p code),
.night-mode .message-content :deep(li code) {
  background-color: #4a5568;
  color: #e2e8f0;
}

.night-mode .message-image {
  background-color: transparent;
}

.night-mode .analysis-button {
  background-color: #6366f1;
}

.night-mode .solution-button {
  background-color: #34d399;
}

.night-mode .action-icon {
  background-color: rgba(255, 255, 255, 0.1);
}

.night-mode .action-icon:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .message-bubble {
    max-width: 90%;
  }
  
  .message-image {
    max-height: 150px;
  }
  
  .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
  
  .grid-3 .message-image:first-child {
    grid-column: span 1;
  }
}
</style>