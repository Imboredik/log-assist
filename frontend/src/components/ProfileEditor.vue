<template>
  <div class="profile-editor">
    <div class="editor-header">
      <button class="back-btn" @click="$emit('cancel')">
        <Icon icon="mdi:arrow-left" width="20" height="20" />
        <span>Редактирование профиля</span>
      </button>
    </div>

    <div class="avatar-editor">
      <div class="avatar-container">
        <div 
          class="avatar-wrapper"
          @click="triggerFileInput"
          @mouseenter="showCameraIcon = true"
          @mouseleave="showCameraIcon = false"
        >
          <div class="avatar" 
            :style="{ 
              backgroundImage: user.avatarUrl ? `url(${user.avatarUrl})` : 'none',
              backgroundColor: !user.avatarUrl ? '#ddd' : 'transparent'
            }">
          </div>
          <div 
            class="camera-icon-wrapper"
            :class="{ 'visible': showCameraIcon }"
          >
            <Icon icon="mdi:camera" width="20" height="20" />
          </div>
          <input 
            type="file" 
            ref="fileInput"
            accept="image/*"
            @change="handleFileChange"
            style="display: none"
          />
        </div>
      </div>

      <div class="avatar-controls">
        <button 
          @click="triggerFileInput" 
          class="avatar-btn change-btn"
        >
          Заменить фото
        </button>
        <button 
          @click="deleteAvatar" 
          class="avatar-btn delete-btn"
          :disabled="!user.avatar_url"
        >
          Удалить фото
        </button>
        <div class="avatar-hint">
          Рекомендуемый размер: 200×200 px<br>
          Максимальный размер: 2 MB
        </div>
      </div>
    </div>

    <form @submit.prevent="saveChanges" class="profile-form">
      <div class="form-group">
        <label>Имя</label>
        <input 
          type="text" 
          v-model="editableName" 
          :disabled="loading"
        />
      </div>

      <div class="form-group">
        <label>Email</label>
        <input 
          type="email" 
          v-model="editableEmail" 
          :disabled="loading"
        />
      </div>

      <div class="password-section" v-if="showPasswordFields">
        <div class="form-group">
          <label>Текущий пароль</label>
          <input 
            type="password" 
            v-model="currentPassword"
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label>Новый пароль</label>
          <input 
            type="password" 
            v-model="newPassword"
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label>Подтвердите пароль</label>
          <input 
            type="password" 
            v-model="confirmPassword"
            :disabled="loading"
          />
        </div>
      </div>

      <div class="form-actions">
        <button 
          type="button" 
          @click="togglePasswordFields"
          class="secondary-btn"
        >
          {{ showPasswordFields ? 'Отмена' : 'Сменить пароль' }}
        </button>
        <button 
          type="submit" 
          :disabled="loading || !hasChanges"
          class="primary-btn"
        >
          <span v-if="loading">Сохранение...</span>
          <span v-else>Сохранить</span>
        </button>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Icon } from '@iconify/vue';
import { useAuthStore } from '@/stores/auth.store';

const authStore = useAuthStore();

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['cancel', 'saved']);

const editableName = ref(props.user.username || '');
const editableEmail = ref(props.user.email || '');
const currentPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const showPasswordFields = ref(false);
const loading = ref(false);
const error = ref(null);
const successMessage = ref(null);
const fileInput = ref(null);
const showCameraIcon = ref(false);

const hasChanges = computed(() => {
  return editableName.value !== props.user.username ||
    editableEmail.value !== props.user.email ||
    (showPasswordFields.value && newPassword.value);
});

const togglePasswordFields = () => {
  showPasswordFields.value = !showPasswordFields.value;
  if (!showPasswordFields.value) {
    currentPassword.value = '';
    newPassword.value = '';
    confirmPassword.value = '';
  }
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileChange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  if (!file.type.match('image.*')) {
    error.value = 'Пожалуйста, выберите файл изображения (PNG, JPG, JPEG)';
    return;
  }

  if (file.size > 2 * 1024 * 1024) {
    error.value = 'Размер файла не должен превышать 2MB';
    return;
  }

  loading.value = true;
  error.value = null;
  try {
    await authStore.updateUserAvatar(file);
    successMessage.value = 'Аватар успешно обновлен';
    setTimeout(() => successMessage.value = null, 3000);
    emit('saved');
  } catch (err) {
    console.error('Avatar upload error:', err);
    error.value = err.response?.data?.detail || 
                 'Не удалось обновить аватар. Пожалуйста, попробуйте снова.';
  } finally {
    loading.value = false;
  }
};

const deleteAvatar = async () => {
  if (!props.user.avatar_url) return;

  loading.value = true;
  error.value = null;
  try {
    await authStore.deleteUserAvatar();
    successMessage.value = 'Аватар успешно удален';
    setTimeout(() => successMessage.value = null, 3000);
    emit('saved'); // Обновляем данные после удаления аватара
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось удалить аватар';
  } finally {
    loading.value = false;
  }
};

const saveChanges = async () => {
  if (!hasChanges.value) return;

  loading.value = true;
  error.value = null;
  successMessage.value = null;

  try {
    // Обновление имени, если изменилось
    if (editableName.value !== props.user.username) {
      await authStore.updateUserName(editableName.value);
    }

    // Обновление email, если изменилось
    if (editableEmail.value !== props.user.email) {
      await authStore.updateUserEmail(editableEmail.value);
    }

    // Обновление пароля, если требуется
    if (showPasswordFields.value && newPassword.value) {
      if (newPassword.value !== confirmPassword.value) {
        throw new Error('Новый пароль и подтверждение не совпадают');
      }
      await authStore.updateUserPassword(currentPassword.value, newPassword.value);
    }

    successMessage.value = 'Изменения успешно сохранены';
    setTimeout(() => {
      successMessage.value = null;
      emit('saved');
    }, 3000);
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Произошла ошибка';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Стили остаются без изменений */
.profile-editor {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.editor-header {
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

.avatar-editor {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  align-items: flex-start;
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border: 3px solid var(--color-border);
  transition: opacity 0.2s ease;
  box-sizing: border-box;
}

.avatar-actions {
  margin-top: 15px;
  display: flex;
  justify-content: center;
}

.avatar:hover {
  opacity: 0.9;
}

.camera-icon-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background-color: rgba(0, 0, 0, 0.4); 
  border-radius: 0 0 60px 60px; 
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
  cursor: pointer;
  border: 3px solid var(--color-border);
  border-top: none; 
  box-sizing: border-box; 
  margin: 0 -3px; 
}

.camera-icon-wrapper.visible {
  opacity: 1;
}

.camera-icon-wrapper:hover {
  background-color: rgba(0, 0, 0, 0.5); 
}

.camera-icon-wrapper :deep(svg) {
  color: white;
  filter: drop-shadow(0 0 1px rgba(0, 0, 0, 0.5));
}

.avatar-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.avatar-btn {
  padding: 8px 16px;
  border-radius: 15px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--color-border);
  background-color: var(--color-background-soft);
}

.change-btn {
  color: #7800FF;
}

.change-btn:hover {
  background-color: rgba(120, 0, 255, 0.1);
}

.delete-btn {
  color: #d32f2f;
}

.delete-btn:hover {
  background-color: rgba(211, 47, 47, 0.1);
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--color-background-soft);
  color: var(--color-text);
}

.avatar-hint {
  font-size: 12px;
  color: var(--color-text);
  opacity: 0.7;
  margin-top: 5px;
}

.profile-form {
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

.form-group input {
  padding: 10px 15px;
  border: 1px solid var(--color-border);
  border-radius: 15px;
  background-color: var(--color-background-soft);
  color: var(--color-text);
}

.form-group input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.password-section {
  padding: 20px;
  background-color: var(--color-background-soft);
  border-radius: 8px;
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 15px;
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
  border-radius: 15px;
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
  border-radius: 15px;
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

.success-message {
  color: #2e7d32;
  padding: 10px;
  background-color: #eeffee;
  border-radius: 6px;
  border: 1px solid #ccffcc;
  margin-top: 15px;
}
</style>