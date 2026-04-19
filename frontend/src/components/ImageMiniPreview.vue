<template>
  <div v-if="images.length > 0" class="image-preview-container">
    <div 
      v-for="(image, index) in images" 
      :key="index"
      class="image-preview-item"
      @mouseenter="hoverIndex = index"
      @mouseleave="hoverIndex = -1"
    >
      <img 
        :src="image.url" 
        :style="{ transform: hoverIndex === index ? 'scale(1.05)' : 'scale(1)' }"
      />
      <button class="remove-image" @click="removeImage(index)">
        <Icon icon="mdi:close" width="16" height="16" color="white" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['remove-image'])

const hoverIndex = ref(-1)

const removeImage = (index) => {
  emit('remove-image', index)
}
</script>

<style scoped>
.image-preview-container {
  position: absolute;
  bottom: 100%;
  left: 0;
  display: inline-flex;
  gap: 8px;
  padding: 12px 16px;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  margin-bottom: 8px;
  max-width: calc(100% - 32px);
  overflow-x: auto;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-preview-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.image-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.remove-image {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.5);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.remove-image:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

/* Стили ночного режима */
.night-mode .image-preview-container {
  background-color: var(--color-background-soft);
  border-color: var(--color-border);
}
</style>