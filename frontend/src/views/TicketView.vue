<template>
  <div class="ticket-view">
    <div class="header">
      <button class="back-btn" @click="goBack">
        <Icon icon="mdi:arrow-left" width="20" height="20" />
        Назад
      </button>
      <h2>Тикет ID-{{ ticket.id }}</h2>
      <div class="meta">
        <span class="priority" :class="'priority-' + ticket.priority_id">
          {{ getPriorityName(ticket.priority_id) }}
        </span>
        <span class="date">
          {{ formatDate(ticket.date_of_create) }}
        </span>
      </div>
    </div>

    <div class="ticket-content">
      <div class="section">
        <h3>Сервис</h3>
        <p>{{ ticket.service || 'Не указан' }}</p>
      </div>

      <div class="section">
        <h3>Краткое описание</h3>
        <p>{{ ticket.summary }}</p>
      </div>

      <div class="section" v-if="ticket.trace">
        <h3>Анализ действий</h3>
        <pre>{{ ticket.trace }}</pre>
      </div>
      <div class="section" v-else>
        <h3>Анализ действий</h3>
        <p>Нет данных о действиях</p>
      </div>

      <!-- Обновленная секция для логов -->
      <div class="section">
        <h3>Логи</h3>
        <div class="logs-container">
          <div class="log-section" v-if="ticket.back_logs">
            <h4>Логи бекенда</h4>
            <div class="log-content">
              <textarea 
                readonly 
                :value="ticket.back_logs"
                placeholder="Нет логов бекенда"
                class="log-textarea"
              />
            </div>
          </div>
          <div class="log-section" v-else>
            <h4>Логи бекенда</h4>
            <p class="no-logs">Нет логов бекенда</p>
          </div>

          <div class="log-section" v-if="ticket.front_logs">
            <h4>Логи фронтенда</h4>
            <div class="log-content">
              <textarea 
                readonly 
                :value="ticket.front_logs"
                placeholder="Нет логов фронтенда"
                class="log-textarea"
              />
            </div>
          </div>
          <div class="log-section" v-else>
            <h4>Логи фронтенда</h4>
            <p class="no-logs">Нет логов фронтенда</p>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="edit-btn" @click="editTicket">
          <Icon icon="mdi:pencil" width="16" height="16" />
          Редактировать
        </button>
        <button class="download-btn" @click="downloadTicket('pdf')">
          <Icon icon="mdi:file-pdf-box" width="16" height="16" />
          Скачать PDF
        </button>
        <button class="download-btn" @click="downloadTicket('csv')">
          <Icon icon="mdi:file-excel-box" width="16" height="16" />
          Скачать CSV
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useTicketStore } from '@/stores/ticket.store'
import api from '@/composables/useApi'

const ticketStore = useTicketStore()
const ticket = computed(() => ticketStore.currentTicket)

const getPriorityName = (priorityId) => {
  const priorities = {
    1: 'низкий',
    2: 'обычный',
    3: 'высокий',
    4: 'критический'
  }
  return priorities[priorityId] || 'неизвестно'
}

const goBack = () => {
  ticketStore.currentTicket = null
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const downloadTicket = async (type) => {
  try {
    const response = await api.downloadTicketFile(ticket.value.id, type) 
    
    // Создаем URL для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `ticket_${ticket.value.id}.${type}`)
    document.body.appendChild(link)
    link.click()
    
    // Очистка
    setTimeout(() => {
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }, 100)
  } catch (error) {
    console.error('Ошибка скачивания тикета:', error)
  }
}

const editTicket = () => {
  ticketStore.isEditorOpen = true
}
</script>

<style scoped>
.ticket-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--color-border);
  position: relative;
}

.header h2 {
  margin-top: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background-color: transparent;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  margin-bottom: 10px;
  transition: color 0.2s;
}

.back-btn:hover {
  color: #7800FF;
}

.meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
  font-size: 14px;
  color: var(--color-text);
  opacity: 0.8;
}

.priority {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
  border: 1px solid currentColor;
}

.priority.priority-1 {
  background-color: var(--priority-low-bg, #e6f7e6);
  color: var(--priority-low, #10b981);
  border-color: var(--priority-low, #10b981);
}

.priority.priority-2 {
  background-color: var(--priority-medium-bg, #f5f5f5);
  color: var(--priority-medium, #757575);
  border-color: var(--priority-medium, #757575);
}

.priority.priority-3 {
  background-color: var(--priority-high-bg, #fff8e1);
  color: var(--priority-high, #f59e0b);
  border-color: var(--priority-high, #f59e0b);
}

.priority.priority-4 {
  background-color: var(--priority-critical-bg, #ffebee);
  color: var(--priority-critical, #ef4444);
  border-color: var(--priority-critical, #ef4444);
}

.ticket-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.section h3 {
  margin-bottom: 8px;
  color: var(--color-text);
}

.section p, .section pre {
  margin: 0;
  color: var(--color-text);
  opacity: 0.9;
  line-height: 1.5;
}

.section pre {
  white-space: pre-wrap;
  font-family: monospace;
  background-color: var(--color-background-soft);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}

/* Стили для секции логов */
.logs-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.log-section h4 {
  margin-bottom: 8px;
  color: var(--color-text);
  font-size: 14px;
  font-weight: 500;
}

.log-content {
  background-color: var(--color-background-soft);
  border-radius: 8px;
  padding: 12px;
}

.log-textarea {
  width: 100%;
  min-height: 120px;
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background-color: var(--color-background);
  color: var(--color-text);
  font-family: monospace;
  font-size: 13px;
  line-height: 1.4;
  resize: vertical;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.log-textarea:read-only {
  cursor: default;
  border-color: var(--color-border);
}

.no-logs {
  color: var(--color-text);
  opacity: 0.6;
  font-style: italic;
  margin: 0;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background-color: var(--chat-button-hover);
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.download-btn:hover {
  background-color: var(--chat-button-hover);
}
</style>