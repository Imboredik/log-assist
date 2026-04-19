<template>
  <div class="dropdown-container">
    <!-- Триггер меню -->
    <div 
      class="dropdown-trigger"
      @mouseenter="showMenu = true"
      @mouseleave="startCloseTimer()"
    >
      <slot name="trigger"></slot>
    </div>

    <!-- Выпадающее меню -->
    <transition name="dropdown">
      <div
        v-show="showMenu"
        class="dropdown-menu"
        @mouseenter="cancelCloseTimer()"
        @mouseleave="startCloseTimer()"
      >
        <div
          v-for="(item, index) in items" 
          :key="index"
          class="menu-item"
          :class="item.class"
          :style="{
            '--hover-bg': item.hoverBgColor || 'var(--dropdown-item-hover-bg)',
            '--hover-text': item.hoverTextColor || 'var(--dropdown-item-hover-text)'
          }"
          @click="handleItemClick(item)"
        >
          <!-- Иконка и текст пункта меню -->
          <span class="menu-item-icon" v-if="item.icon">
            <Icon :icon="item.icon" v-if="isIconifyIcon(item.icon)" />
            <component :is="item.icon" v-else-if="typeof item.icon === 'object'" />
            <i :class="item.icon" v-else-if="typeof item.icon === 'string'" />
          </span>
          <span class="menu-item-label">{{ item.label }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => [],
    validator: (items) => {
      return items.every(item => {
        return 'label' in item && (typeof item.label === 'string')
      })
    }
  },
  align: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'right', 'center'].includes(value)
  }
})

const emit = defineEmits(['item-click'])

const showMenu = ref(false)
let closeTimer = null
const CLOSE_DELAY = 150

const isIconifyIcon = (icon) => {
  return typeof icon === 'string' && (icon.includes(':') || icon.includes('/'))
}

const startCloseTimer = () => {
  clearTimeout(closeTimer)
  closeTimer = setTimeout(() => {
    showMenu.value = false
  }, CLOSE_DELAY)
}

const cancelCloseTimer = () => {
  clearTimeout(closeTimer)
}

const handleItemClick = (item) => {
  showMenu.value = false
  emit('item-click', item)
}
</script>

<style scoped>
.dropdown-container {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  font-family: 'RostelecomBasis', sans-serif;
  font-weight: 400;
  background-color: var(--dropdown-bg);
  border: 1px solid var(--dropdown-border);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  width: max-content;
  min-width: 180px;
  max-width: 300px;
  margin-top: 8px;
  overflow: hidden;
  right: v-bind('align === "right" ? "0" : "auto"');
  left: v-bind('align === "left" ? "0" : "auto"');
  transform-origin: top center;
}

.menu-item {
  font-family: inherit;
  font-weight: inherit;
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 12px;
  font-size: 14px;
  color: var(--dropdown-item-text);
}

.menu-item:hover {
  background-color: var(--hover-bg);
  color: var(--hover-text);
}

.menu-item:hover .menu-item-icon {
  color: var(--hover-text);
}

.menu-item-icon {
  display: inline-flex;
  width: 18px;
  height: 18px;
  color: var(--dropdown-icon-color);
  transition: color 0.2s ease;
}

.menu-item-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: inherit;
  font-weight: inherit;
}

/* Анимации */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.menu-item.danger {
  color: var(--danger-item-text);
}

.menu-item.danger .menu-item-icon {
  color: var(--danger-item-text);
}

.menu-item.danger:hover {
  background-color: var(--danger-item-hover-bg);
  color: var(--danger-item-hover-text);
}

.menu-item.danger:hover .menu-item-icon {
  color: var(--danger-item-hover-text);
}

/* Ночной режим */
.night-mode .dropdown-menu {
  background-color: var(--dropdown-bg-night);
  border-color: var(--dropdown-border-night);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.night-mode .menu-item {
  color: var(--dropdown-item-text-night);
}

.night-mode .menu-item-icon {
  color: var(--dropdown-icon-color-night);
}

.night-mode .menu-item.danger {
  color: var(--danger-item-text-night);
}

.night-mode .menu-item.danger .menu-item-icon {
  color: var(--danger-item-text-night);
}

.night-mode .menu-item.danger:hover {
  background-color: var(--danger-item-hover-bg-night);
  color: var(--danger-item-hover-text-night);
}

.night-mode .menu-item.danger:hover .menu-item-icon {
  color: var(--danger-item-hover-text-night);
}
</style>