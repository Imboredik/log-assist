<template>
  <div class="ticket-button-container" @mouseenter="onMouseEnter" @mouseleave="onMouseLeave">
    <button 
      class="ticket-button"
      @click="handleClick"
      :disabled="loading"
      :class="{ active: isActive }"
    >
      <span v-if="loading">
        <Icon icon="mdi:loading" class="spin" /> Загрузка...
      </span>
      <span v-else class="ticket-content">
        <span class="ticket-id">#{{ ticket.id }}</span>
        <span class="ticket-priority" :class="'priority-' + ticket.priority_id">
          {{ getPriorityName(ticket.priority_id) }}
        </span>
        <span class="ticket-summary">
          {{ truncateSummary(ticket.summary) }}
        </span>
        <span class="ticket-date">
          {{ formatDate(ticket.date_of_create) }}
        </span>
      </span>
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
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import DropdownMenu from './DropdownMenu.vue'
import { useTicketStore } from '@/stores/ticket.store'
import api from '@/composables/useApi'

const props = defineProps({
  ticket: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['ticket-selected'])

const ticketStore = useTicketStore()

const loading = ref(false)
const showMenuButton = ref(false)
const isMenuOpen = ref(false)

const menuItems = ref([
  { label: 'Скачать PDF', action: 'download-pdf', icon: 'mdi:file-pdf-box' },
  { label: 'Скачать CSV', action: 'download-csv', icon: 'mdi:file-excel-box' }
])

const shouldShowMenu = computed(() => {
  return props.isActive || (showMenuButton.value && !isMenuOpen.value)
})

const getPriorityName = (priorityId) => {
  const priorities = {
    1: 'низкий',
    2: 'обычный',
    3: 'высокий',
    4: 'критический'
  }
  return priorities[priorityId] || 'неизвестно'
}

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

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const handleClick = async () => {
    loading.value = true;
    try {
        const success = await ticketStore.openTicketView(props.ticket.id);
        if (success) {
            emit('ticket-selected', props.ticket);
        }
    } catch (error) {
        console.error('Ошибка загрузки тикета:', error);
    } finally {
        loading.value = false;
    }
}

const handleMenuClick = async (item) => {
  if (item.action === 'download-pdf') {
    await downloadTicket('pdf')
  } else if (item.action === 'download-csv') {
    await downloadTicket('csv')
  }
  isMenuOpen.value = false
}

const downloadTicket = async (type) => {
  try {
    await api.downloadTicketFile(props.ticket.id, type)
  } catch (error) {
    console.error('Ошибка скачивания тикета:', error)
  }
}

const truncateSummary = (summary) => {
  if (!summary) return 'Без описания';
  return summary.length > 20 ? summary.substring(0, 20) + '...' : summary;
}
</script>


<style scoped>
.ticket-button-container {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0 8px;
  box-sizing: border-box;
  position: relative;
}

.ticket-button {
  width: 100%;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  border: none;
  background-color: transparent;
  transition: background-color 0.2s;
  color: inherit;
  display: flex;
  align-items: center;
  height: 36px;
  white-space: nowrap;
  overflow: hidden;
  position: relative;
  padding-right: 40px;
}

.ticket-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  overflow: hidden;
}

.ticket-id {
  font-weight: 500;
  flex-shrink: 0;
}

.ticket-priority {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: capitalize;
  flex-shrink: 0;
  border: 1px solid currentColor;
}

.ticket-priority.priority-1 {
  background-color: var(--priority-low-bg, #e6f7e6);
  color: var(--priority-low, #10b981);
  border-color: var(--priority-low, #10b981);
}

.ticket-priority.priority-2 {
  background-color: var(--priority-medium-bg, #f5f5f5);
  color: var(--priority-medium, #757575);
  border-color: var(--priority-medium, #757575);
}

.ticket-priority.priority-3 {
  background-color: var(--priority-high-bg, #fff8e1);
  color: var(--priority-high, #f59e0b);
  border-color: var(--priority-high, #f59e0b);
}

.ticket-priority.priority-4 {
  background-color: var(--priority-critical-bg, #ffebee);
  color: var(--priority-critical, #ef4444);
  border-color: var(--priority-critical, #ef4444);
}

.ticket-summary {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.9;
  min-width: 0;
}

.ticket-date {
  font-size: 12px;
  opacity: 0.7;
  flex-shrink: 0;
  margin-right: 8px;
}

.menu-button-wrapper {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
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

.ticket-button:hover {
  background-color: var(--chat-button-hover);
}

.ticket-button:disabled {
  background-color: rgba(238, 238, 238, 0.5);
  cursor: not-allowed;
}

.ticket-button.active {
  background-color: var(--chat-button-active);
  font-weight: 500;
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