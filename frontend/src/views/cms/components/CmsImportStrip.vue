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
    <div v-if="loading" class="upload-progress import-progress">
      <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined" />
      <span>{{ progress < 100 ? uploadingText : processingText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

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
  if (file) emit('import', file)
  input.value = ''
}
</script>

