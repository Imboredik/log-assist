<template>
  <div class="role-selection">
    <h3>Выберите вашу роль</h3>
    <div class="role-options">
      <div 
        v-for="role in roles" 
        :key="role.id" 
        class="role-card"
        :class="{ 'selected': selectedRole === role.id }"
        @click="selectRole(role)"
      >
        <h4>{{ role.role }}</h4>
        <p>{{ role.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  roles: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const selectedRole = ref(props.modelValue)

const selectRole = (role) => {
  selectedRole.value = role.id
  emit('update:modelValue', role.id)
}
</script>

<style scoped>
.role-selection {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.role-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.role-card {
  padding: 20px;
  border-radius: 15px;
  border: 1px solid var(--input-border);
  background-color: var(--input-bg);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 10px;
}

.role-card:hover {
  border-color: #7800FF;
}

.role-card.selected {
  border-color: #7800FF;
  background-color: rgba(120, 0, 255, 0.1);
}

.role-card h4 {
  margin: 0;
  color: #7800FF;
}

.role-card p {
  margin: 0;
  font-size: 14px;
  color: var(--color-text);
}
</style>