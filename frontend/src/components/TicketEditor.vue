<template>
  <div class="ticket-editor">
    <div class="header">
      <button class="back-btn" @click="cancel">
        <Icon icon="mdi:arrow-left" width="20" height="20" />
        <span>{{ ticketId ? 'Редактирование тикета' : 'Создание тикета' }}</span>
      </button>
    </div>

    <form @submit.prevent="save" class="ticket-form">
      <div class="form-group">
        <label>Приоритет проблемы</label>
        <DropdownMenu :items="priorityItems" align="left" @item-click="selectPriority">
            <template #trigger>
            <button class="priority-trigger">
                <span class="priority-label" :style="{ color: selectedPriorityColor }">
                {{ selectedPriorityName }}
                </span>
                <Icon icon="mdi:chevron-down" width="20" height="20" />
            </button>
            </template>
        </DropdownMenu>
      </div>

      <div class="form-group">
        <label>Сервис</label>
        <input 
          type="text" 
          v-model="formData.service"
          placeholder="Укажите сервис, в котором возникла проблема"
        />
      </div>

      <div class="form-group">
        <label>Краткое описание</label>
        <textarea 
          v-model="formData.summary"
          placeholder="Опишите проблему кратко"
        />
      </div>

      <div class="form-group">
        <label>Анализ действий</label>
        <textarea 
          v-model="formData.trace"
          placeholder="Добавьте историю действий"
        />
      </div>

      <div class="form-group">
        <label>Логи бекенда</label>
        <textarea 
          v-model="formData.back_logs"
          placeholder="Добавьте логи бекенда, если необходимо"
          rows="4"
        />
      </div>

      <div class="form-group">
        <label>Логи фронтенда</label>
        <textarea 
          v-model="formData.front_logs"
          placeholder="Добавьте логи фронтенда, если необходимо"
          rows="4"
        />
      </div>

      <div class="form-actions">
        <button 
          type="button" 
          @click="cancel"
          class="secondary-btn"
        >
          Отмена
        </button>
        <button 
          type="submit" 
          :disabled="loading"
          class="primary-btn"
        >
          <span v-if="loading">Сохранение...</span>
          <span v-else>{{ ticketId ? 'Обновить тикет' : 'Создать тикет' }}</span>
        </button>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useTicketStore } from '@/stores/ticket.store'
import DropdownMenu from '@/components/DropdownMenu.vue'
import api from '@/composables/useApi'

const ticketStore = useTicketStore()
const emit = defineEmits(['saved', 'cancel'])

const loading = ref(false)
const error = ref(null)
const priorities = ref([])
const selectedPriority = ref(null)
const formData = ref({
  chat_id: null,
  priority_id: 2,
  service: '',
  summary: '',
  trace: '',
  back_logs: '',
  front_logs: ''
})


const ticketId = computed(() => ticketStore.currentTicket?.id)

const priorityItems = computed(() => {
  return priorities.value.map(priority => ({
    id: priority.priority_id,
    label: priority.name,      
    value: priority.priority_id,
    class: `priority-${priority.priority_id}`,
    hoverBgColor: getPriorityColorById(priority.priority_id, 'hover'),
    hoverTextColor: 'white'
  }));
});

const selectedPriorityName = computed(() => {
  if (selectedPriority.value) {
    return selectedPriority.value.name 
  }
  const defaultPriority = priorities.value.find(p => p.priority_id === formData.value.priority_id)
  return defaultPriority ? defaultPriority.name : 'Выберите приоритет' 
})

const getPriorityColorById = (priorityId, type = 'normal') => {
  const colors = {
    normal: {
      1: '#10b981', // зеленый - низкий
      2: '#757575', // серый - обычный
      3: '#f59e0b', // желтый - серьезный
      4: '#ef4444'  // красный - критический
    },
    hover: {
      1: '#059669', // темно-зеленый
      2: '#616161', // темно-серый
      3: '#d97706', // темно-желтый
      4: '#dc2626'  // темно-красный
    }
  };

  return colors[type][priorityId] || 'var(--color-text)';
}

const selectedPriorityColor = computed(() => {
  const priorityId = selectedPriority.value?.priority_id || formData.value.priority_id;
  return getPriorityColorById(priorityId);
});

const selectPriority = (item) => {
  selectedPriority.value = priorities.value.find(p => p.priority_id === item.id)
  formData.value.priority_id = item.id
}

// Замените получение приоритетов в onMounted
onMounted(async () => {
  if (ticketStore.currentTicket) {
    formData.value = {
      chat_id: ticketStore.currentTicket.chat_id,
      priority_id: ticketStore.currentTicket.priority_id || 2,
      service: ticketStore.currentTicket.service || '',
      summary: ticketStore.currentTicket.summary || '',
      trace: ticketStore.currentTicket.trace || '',
      back_logs: ticketStore.currentTicket.back_logs || '',
      front_logs: ticketStore.currentTicket.front_logs || ''
    }
  }
  
  // Загружаем приоритеты
  try {
    const response = await api.getPriorities()
    priorities.value = response.data
    
    // Устанавливаем выбранный приоритет
    if (formData.value.priority_id) {
      selectedPriority.value = priorities.value.find(p => p.priority_id === formData.value.priority_id)
    }
  } catch (err) {
    error.value = 'Не удалось загрузить приоритеты'
    console.error('Ошибка загрузки приоритетов:', err)
  }
})

const save = async () => {
  if (!formData.value.chat_id || !formData.value.priority_id) {
    error.value = 'Выберите приоритет';
    return;
  }

  loading.value = true;
  error.value = null;
  
  try {
    const ticketData = {
      chat_id: formData.value.chat_id,
      priority_id: formData.value.priority_id,
      service: formData.value.service || "",
      summary: formData.value.summary,
      trace: formData.value.trace,
      logs: formData.value.logs,
    };
    
    const success = await ticketStore.saveTicket(ticketData);
    
    if (success) {
      emit('saved');
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка сохранения тикета';
    console.error('Ошибка сохранения:', err);
  } finally {
    loading.value = false;
  }
}


const cancel = () => {
  if (hasUnsavedChanges()) {
    if (!confirm('Вы действительно хотите закрыть редактор? Все несохраненные изменения будут потеряны.')) {
      return;
    }
  }
  resetForm();
  ticketStore.resetCurrentTicket();
  emit('cancel');
}

const hasUnsavedChanges = () => {
  if (!ticketStore.currentTicket) {
    // Новый тикет
    return formData.value.summary || formData.value.trace || formData.value.logs;
  }
  
  // Редактирование существующего тикета
  return (
    formData.value.summary !== ticketStore.currentTicket.summary ||
    formData.value.trace !== ticketStore.currentTicket.trace ||
    formData.value.logs !== ticketStore.currentTicket.logs ||
    formData.value.priority_id !== ticketStore.currentTicket.priority_id
  );
}

const resetForm = () => {
  formData.value = {
    chat_id: null,
    priority_id: 1,
    service: '',
    summary: '',
    trace: '',
    logs: ''
  }
  selectedPriority.value = null;
}

</script>

<style scoped>
.ticket-editor {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  margin-bottom: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text);
  padding: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.back-btn:hover {
  color: #7800FF;
}

.ticket-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 15px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-background-soft);
  color: var(--color-text);
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.primary-btn {
  padding: 10px 20px;
  background-color: #7800FF;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.primary-btn:hover {
  background-color: #6000CC;
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #cccccc;
}

.secondary-btn {
  padding: 10px 20px;
  background-color: transparent;
  color: #7800FF;
  border: 1px solid #7800FF;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.secondary-btn:hover {
  background-color: rgba(120, 0, 255, 0.1);
}

.error-message {
  color: #d32f2f;
  padding: 10px;
  background-color: #ffeeee;
  border-radius: 6px;
  border: 1px solid #ffcccc;
  margin-top: 15px;
}

.priority-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px 15px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-background-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.priority-trigger:hover {
  border-color: var(--color-border-hover);
}

.priority-label {
  margin-right: 8px;
  font-weight: 500;
}

/* Стили для приоритетов в выпадающем меню */
:deep(.priority-1) { color: #10b981; }
:deep(.priority-2) { color: #757575; } 
:deep(.priority-3) { color: #f59e0b; } 
:deep(.priority-4) { color: #ef4444; } 

:deep(.priority-1:hover) { background-color: #059669 !important; color: white !important; }
:deep(.priority-2:hover) { background-color: #616161 !important; color: white !important; }
:deep(.priority-3:hover) { background-color: #d97706 !important; color: white !important; }
:deep(.priority-4:hover) { background-color: #dc2626 !important; color: white !important; }
</style>