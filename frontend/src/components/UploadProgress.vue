<template>
  <div v-if="active || progress > 0" class="upload-progress-panel" role="status" aria-live="polite">
    <el-progress :percentage="normalizedProgress" :status="normalizedProgress === 100 ? 'success' : undefined" />
    <span>{{ normalizedProgress < 100 ? uploadingText : processingText }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

.upload-progress-panel span {
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.45;
}
</style>
