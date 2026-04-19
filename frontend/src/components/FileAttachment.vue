<template>
  <div class="file-attachment" @click="openFile">
    <div class="file-icon">
      <Icon :icon="fileIcon" width="24" height="24" />
    </div>
    <div class="file-name" :title="file.name">
      {{ truncatedFileName }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  file: {
    type: Object,
    required: true
  }
})

const fileIcon = computed(() => {
  const extension = props.file.name.split('.').pop().toLowerCase()
  switch(extension) {
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
    case 'webp':
      return 'octicon:image-16'
    case 'pdf':
      return 'vscode-icons:file-type-pdf2'
    case 'doc':
    case 'docx':
      return 'vscode-icons:file-type-word2'
    case 'xls':
    case 'xlsx':
      return 'vscode-icons:file-type-excel2'
    case 'zip':
    case 'rar':
      return 'vscode-icons:file-type-zip'
    default:
      return 'octicon:file-16'
  }
})

const truncatedFileName = computed(() => {
  const maxLength = 20
  if (props.file.name.length > maxLength) {
    return props.file.name.substring(0, maxLength - 3) + '...'
  }
  return props.file.name
})

const openFile = () => {
  window.open(props.file.url, '_blank')
}
</script>

<style scoped>
.file-attachment {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  width: 100%;
  height: 100%;
  margin-bottom: 0;
}

.file-attachment:hover {
  background-color: var(--chat-button-hover);
}

.file-icon {
  margin-right: 12px;
  color: var(--color-text);
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-text);
  font-size: 14px;
}
</style>