<template>
  <div class="image-preview-container" v-if="show" @click.self="close">
    <div class="image-preview-content">
      <button class="close-btn" @click="close">
        <Icon icon="mdi:close" width="24" height="24" />
      </button>
      <img :src="currentImage" class="preview-image" alt="Preview" />
      <div class="navigation-buttons" v-if="images.length > 1">
        <button @click="prevImage" class="nav-btn prev-btn">
          <Icon icon="mdi:chevron-left" width="24" height="24" />
        </button>
        <button @click="nextImage" class="nav-btn next-btn">
          <Icon icon="mdi:chevron-right" width="24" height="24" />
        </button>
      </div>
      <div class="image-counter" v-if="images.length > 1">
        {{ currentIndex + 1 }} / {{ images.length }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  }
})

const show = ref(false)
const currentIndex = ref(0)

const currentImage = computed(() => {
  return props.images[currentIndex.value]
})

const open = (index = 0) => {
  currentIndex.value = index
  show.value = true
  document.body.style.overflow = 'hidden'
}

const close = () => {
  show.value = false
  document.body.style.overflow = ''
}

const nextImage = () => {
  currentIndex.value = (currentIndex.value + 1) % props.images.length
}

const prevImage = () => {
  currentIndex.value = (currentIndex.value - 1 + props.images.length) % props.images.length
}

defineExpose({
  open
})
</script>

<style scoped>
.image-preview-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000; /* Увеличиваем z-index чтобы перекрыть sidebar и panel */
  cursor: pointer;
}

.image-preview-content {
  position: relative;
  width: 70%; /* Уменьшаем ширину контейнера */
  max-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh; /* Уменьшаем максимальную высоту изображения */
  object-fit: contain;
  border-radius: 8px;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 24px;
}

.navigation-buttons {
  position: absolute;
  width: 100%;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.nav-btn {
  pointer-events: auto;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin: 0 20px;
}

.image-counter {
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  font-size: 16px;
  background: rgba(0, 0, 0, 0.5);
  padding: 5px 15px;
  border-radius: 20px;
}

@media (max-width: 768px) {
  .image-preview-content {
    width: 90%;
    max-height: 80vh;
  }
  
  .preview-image {
    max-height: 70vh;
  }
  
  .nav-btn {
    margin: 0 10px;
    width: 30px;
    height: 30px;
  }
}
</style>