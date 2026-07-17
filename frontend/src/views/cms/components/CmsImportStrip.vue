<template>
  <div class="cms-import-block">
    <div class="import-strip">
      <span>{{ description }}，Excel 不超过 50 MB</span>
      <a :href="templateUrl" download>下载模板</a>
      <button type="button" :disabled="loading" @click="inputRef?.click()">
        {{ loading ? '正在导入' : '导入 Excel' }}
      </button>
      <input ref="inputRef" type="file" accept=".xlsx" @change="handleFile" />
    </div>
    <FeedbackPanel v-if="loading" type="processing" title="正在导入" description="上传和写入完成前请保持当前页面打开。">
      <UploadProgress :active="loading" :progress="progress" :uploading-text="uploadingText" :processing-text="processingText" />
    </FeedbackPanel>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import FeedbackPanel from '../../../components/FeedbackPanel.vue'
import { UPLOAD_LIMIT, validateUploadFile } from '../../../utils/files'
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
    const message = validateUploadFile(file, UPLOAD_LIMIT.spreadsheet)
    if (message) ElMessage.warning(message)
    else emit('import', file)
  }
  input.value = ''
}
</script>
