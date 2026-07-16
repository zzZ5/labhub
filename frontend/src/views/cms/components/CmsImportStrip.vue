<template>
  <div class="cms-import-block">
    <div class="import-strip">
      <span>{{ description }}</span>
      <a :href="templateUrl" download>下载模板</a>
      <button type="button" :disabled="loading" @click="inputRef?.click()">
        {{ loading ? '正在导入' : '导入 Excel' }}
      </button>
      <input ref="inputRef" type="file" accept=".xlsx" @change="handleFile" />
    </div>
    <UploadProgress :active="loading" :progress="progress" :uploading-text="uploadingText" :processing-text="processingText" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import { validateUploadFile } from '../../../utils/files'
import { ElMessage } from 'element-plus'

defineProps<{
  description: string
  templateUrl: string
  loading: boolean
  progress: number
  uploadingText: string
  processingText: string
}>()

const emit = defineEmits<{
  import: [file: File]
}>()

const inputRef = ref<HTMLInputElement | null>(null)

function handleFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    const message = validateUploadFile(file)
    if (message) ElMessage.warning(message)
    else emit('import', file)
  }
  input.value = ''
}
</script>
