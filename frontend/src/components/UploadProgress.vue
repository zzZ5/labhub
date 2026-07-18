<template>
  <div v-if="active || progress > 0" class="upload-progress-panel" role="status" aria-live="polite">
    <el-progress :percentage="normalizedProgress" :status="!active && normalizedProgress === 100 ? 'success' : undefined" />
    <div class="upload-progress-copy">
      <span>{{ normalizedProgress < 100 ? uploadingText : processingText }}</span>
      <button v-if="active && normalizedProgress > 0 && normalizedProgress < 100" type="button" @click="cancelUpload">取消上传</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

import { cancelActiveUploads } from '../api/http'

const props = withDefaults(defineProps<{
  active?: boolean
  progress: number
  uploadingText?: string
  processingText?: string
}>(), {
  active: false,
  uploadingText: '正在上传，请不要关闭页面。',
  processingText: '上传完成，正在保存。',
})

const normalizedProgress = computed(() => Math.min(100, Math.max(0, Math.round(props.progress))))

function cancelUpload() {
  if (cancelActiveUploads()) ElMessage.info('正在取消上传。')
}
</script>

<style scoped>
.upload-progress-panel {
  display: grid;
  gap: 7px;
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
  padding: 11px 12px;
  background: var(--color-soft-gray);
  text-align: left;
}

.upload-progress-copy {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.upload-progress-panel span {
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.45;
}

.upload-progress-copy button {
  flex: 0 0 auto;
  border: 0;
  padding: 2px 0;
  background: transparent;
  color: #9f312f;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
}

.upload-progress-copy button:hover {
  text-decoration: underline;
}
</style>
