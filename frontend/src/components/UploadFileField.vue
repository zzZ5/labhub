<template>
  <div class="upload-file-field">
    <label
      :class="['upload-dropzone', { dragging, disabled }]"
      @dragenter.prevent="dragging = true"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="handleDrop"
    >
      <input ref="inputRef" type="file" :accept="accept" :disabled="disabled" @change="handleInput" />
      <el-icon><UploadFilled /></el-icon>
      <span>{{ dragging ? '松开即可选择文件' : '点击选择或拖入文件' }}</span>
      <small>{{ hint || `单个文件不超过 ${maxSizeMb} MB` }}</small>
    </label>
    <div v-if="modelValue" class="selected-file">
      <div><strong :title="modelValue.name">{{ modelValue.name }}</strong><span>{{ formatFileSize(modelValue.size) }}</span></div>
      <button type="button" :disabled="disabled" @click="clear">移除</button>
    </div>
    <div v-else-if="existingLabel" class="selected-file existing">
      <div><strong :title="existingLabel">{{ existingLabel }}</strong><span>未选择新文件时保留当前文件</span></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { formatFileSize, validateUploadFile } from '../utils/files'

const props = withDefaults(defineProps<{
  modelValue?: File
  accept?: string
  existingLabel?: string
  hint?: string
  maxSizeMb?: number
  disabled?: boolean
}>(), { accept: '', existingLabel: '', hint: '', maxSizeMb: 20, disabled: false })
const emit = defineEmits<{ 'update:modelValue': [file: File | undefined]; error: [message: string] }>()
const inputRef = ref<HTMLInputElement | null>(null)
const dragging = ref(false)

function select(file?: File) {
  if (!file) return
  const message = validateUploadFile(file, props.maxSizeMb * 1024 * 1024)
  if (message) {
    ElMessage.warning(message)
    emit('error', message)
    return
  }
  emit('update:modelValue', file)
}

function handleInput(event: Event) {
  select((event.target as HTMLInputElement).files?.[0])
}

function handleDrop(event: DragEvent) {
  dragging.value = false
  if (!props.disabled) select(event.dataTransfer?.files?.[0])
}

function clear() {
  if (inputRef.value) inputRef.value.value = ''
  emit('update:modelValue', undefined)
}

watch(() => props.modelValue, (file) => {
  if (!file && inputRef.value) inputRef.value.value = ''
})
</script>

<style scoped>
.upload-file-field {
  display: grid;
  gap: 9px;
  width: 100%;
}

.upload-dropzone {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 3px 10px;
  width: 100%;
  border: 1px dashed #b9c9bf;
  border-radius: var(--radius-sm);
  padding: 13px 14px;
  background: #fafcfb;
  color: var(--color-deep-green);
  cursor: pointer;
}

.upload-dropzone:hover,
.upload-dropzone.dragging {
  border-color: var(--color-cau-green);
  background: var(--color-eco-green);
}

.upload-dropzone.disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.upload-dropzone input {
  display: none;
}

.upload-dropzone .el-icon {
  grid-row: 1 / span 2;
  color: var(--color-cau-green);
  font-size: 22px;
}

.upload-dropzone span {
  overflow: hidden;
  font-size: 14px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-dropzone small,
.selected-file span {
  color: var(--color-muted);
  font-size: 12px;
}

.selected-file {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 9px 11px;
  background: #fff;
}

.selected-file > div {
  display: grid;
  min-width: 0;
  overflow: hidden;
  gap: 2px;
}

.selected-file strong {
  overflow: hidden;
  color: var(--color-text);
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-file button {
  flex: 0 0 auto;
  border: 0;
  padding: 4px;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  font-size: 12px;
}

.selected-file button:hover {
  color: #9f312f;
}

@media (max-width: 480px) {
  .selected-file {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 8px;
  }

  .selected-file strong,
  .selected-file span {
    max-width: 100%;
  }
}
</style>
