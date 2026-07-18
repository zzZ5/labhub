<template>
  <div class="cms-import-block">
    <div class="import-strip">
      <span>{{ description }}，Excel 不超过 50 MB</span>
      <a :href="templateUrl" download>下载模板</a>
      <button type="button" :disabled="loading || completed" @click="inputRef?.click()">
        {{ completed ? '本次已导入' : loading ? '正在导入' : '导入 Excel' }}
      </button>
      <input ref="inputRef" type="file" accept=".xlsx" :disabled="loading || completed" @change="handleFile" />
    </div>
    <FeedbackPanel v-if="loading" type="processing" title="正在导入" description="上传和写入完成前请保持当前页面打开。">
      <UploadProgress :active="loading" :progress="progress" :uploading-text="uploadingText" :processing-text="processingText" />
    </FeedbackPanel>
    <div v-else-if="completed" class="import-complete" role="status">
      <span>本次文件已导入，为避免重复写入已暂停再次提交。</span>
      <button type="button" @click="emit('reset')">导入另一份文件</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import FeedbackPanel from '../../../components/FeedbackPanel.vue'
import { UPLOAD_LIMIT, validateUploadFile } from '../../../utils/files'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  description: string
  templateUrl: string
  loading: boolean
  progress: number
  uploadingText: string
  processingText: string
  completed: boolean
}>()

const emit = defineEmits<{
  import: [file: File]
  reset: []
}>()

const inputRef = ref<HTMLInputElement | null>(null)

function handleFile(event: Event) {
  const input = event.target as HTMLInputElement
  if (props.loading || props.completed) {
    input.value = ''
    return
  }
  const file = input.files?.[0]
  if (file) {
    const message = validateUploadFile(file, UPLOAD_LIMIT.spreadsheet)
    if (message) ElMessage.warning(message)
    else emit('import', file)
  }
  input.value = ''
}
</script>

<style scoped>
.import-complete {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  border: 1px solid var(--color-success-border);
  border-radius: var(--radius-sm);
  padding: 9px 12px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 12px;
}

.import-complete button {
  flex: 0 0 auto;
  border: 0;
  padding: 2px 0;
  background: transparent;
  color: var(--color-cau-green);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

@media (max-width: 720px) {
  .import-complete {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
