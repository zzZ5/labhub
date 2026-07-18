<template>
  <article class="file-info-row">
    <div :class="['file-kind-icon', kind]"><el-icon><component :is="icon" /></el-icon></div>
    <div class="file-info-copy">
      <div class="file-title-line"><strong :title="title">{{ title }}</strong><span>{{ typeLabel }}</span></div>
      <div class="file-meta">
        <span v-if="filename" :title="filename">{{ displayFilename }}</span>
        <span v-if="size">{{ formatFileSize(size) }}</span>
        <time v-if="uploadedAt" :datetime="uploadedAt">{{ formatDate(uploadedAt) }}</time>
        <span v-if="status">{{ status }}</span>
      </div>
      <p v-if="description">{{ description }}</p>
    </div>
    <div class="file-info-actions"><slot name="actions" /></div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Document, Files, PictureFilled, VideoCamera } from '@element-plus/icons-vue'
import { formatFileSize, middleEllipsisFilename } from '../utils/files'

const props = withDefaults(defineProps<{ title: string; filename?: string; size?: number; description?: string; mimeType?: string; uploadedAt?: string; status?: string }>(), {
  filename: '', size: 0, description: '', mimeType: '', uploadedAt: '', status: '',
})
const displayFilename = computed(() => middleEllipsisFilename(props.filename))
const kind = computed(() => {
  const value = `${props.filename} ${props.mimeType}`.toLowerCase()
  if (/\.pdf\b|application\/pdf/.test(value)) return 'pdf'
  if (/\.docx?\b|word/.test(value)) return 'word'
  if (/\.pptx?\b|presentation/.test(value)) return 'ppt'
  if (/\.xlsx?\b|spreadsheet|excel/.test(value)) return 'excel'
  if (/\.(png|jpe?g|gif|webp)\b|image\//.test(value)) return 'image'
  if (/\.(mp4|webm|mov)\b|video\//.test(value)) return 'video'
  return 'file'
})
const typeLabel = computed(() => ({ pdf: 'PDF', word: 'Word', ppt: 'PPT', excel: 'Excel', image: '图片', video: '视频', file: '文件' })[kind.value])
const icon = computed(() => kind.value === 'image' ? PictureFilled : kind.value === 'video' ? VideoCamera : kind.value === 'ppt' ? Files : Document)

function formatDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(date)
}
</script>

<style scoped>
.file-info-row {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr) auto;
  align-items: center;
  gap: 11px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 10px 11px;
  background: var(--color-panel);
}

.file-info-row:hover { border-color: rgba(0, 135, 60, 0.18); background: #fff; }
.file-kind-icon { display: grid; width: 34px; height: 34px; place-items: center; border: 1px solid var(--color-line); border-radius: var(--radius-sm); background: #fff; color: var(--color-academic-blue); }
.file-kind-icon.pdf { background: #fff5f5; color: #9f312f; }
.file-kind-icon.word { background: #eff6ff; color: #315f8f; }
.file-kind-icon.ppt { background: #fff7ed; color: #a65f2b; }
.file-kind-icon.excel { background: var(--color-eco-green); color: var(--color-cau-green-dark); }
.file-kind-icon.image { background: var(--color-eco-green); color: var(--color-cau-green); }
.file-kind-icon.video { background: rgba(173, 200, 202, 0.22); color: var(--color-cau-wisdom-blue); }
.file-info-copy { min-width: 0; }
.file-title-line, .file-meta, .file-info-actions { display: flex; align-items: center; gap: 8px; }
.file-title-line strong, .file-meta span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-title-line strong { color: var(--color-deep-green); font-size: 14px; }
.file-title-line span, .file-meta { color: var(--color-muted); font-size: 12px; }
.file-meta > * + *::before { margin-right: 8px; color: var(--color-border); content: '·'; }
.file-info-copy p { overflow: hidden; margin: 3px 0 0; color: var(--color-muted); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.file-info-actions { justify-content: flex-end; white-space: nowrap; }

@media (max-width: 760px) {
  .file-info-row { grid-template-columns: 36px minmax(0, 1fr); }
  .file-info-actions { grid-column: 1 / -1; flex-wrap: wrap; justify-content: flex-start; }
}
</style>
