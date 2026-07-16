<template>
  <section class="card files-panel">
    <div class="panel-heading">
      <div>
        <h2>归档资料</h2>
        <p>用于保存开题、中期、毕业论文、答辩材料和其它个人归档资料。</p>
      </div>
      <span class="status-tag normal">{{ files.length }} 份资料</span>
    </div>

    <div v-if="files.length" class="file-grid">
      <article v-for="file in files" :key="file.id" class="file-card">
        <div class="file-icon" :class="archiveKind(file)">
          <el-icon><component :is="archiveIcon(file)" /></el-icon>
        </div>
        <div class="file-main">
          <div class="file-title-row">
            <strong>{{ file.title }}</strong>
            <span>{{ archiveTypeLabel(file) }}</span>
          </div>
          <div class="file-meta">
            <span>{{ file.file_type_label }}</span>
            <span>{{ archiveFileSizeLabel(file) }}</span>
          </div>
          <p>{{ file.description || file.original_filename || '未记录原始文件名' }}</p>
        </div>
        <div class="file-actions">
          <a v-if="canPreviewArchive(file)" class="file-primary-action" :href="previewStudentArchiveFileUrl(file)" target="_blank" rel="noreferrer">
            <el-icon><View /></el-icon>{{ archivePreviewLabel(file) }}
          </a>
          <span v-else class="file-preview-note">{{ archivePreviewStatus(file) }}</span>
          <a class="file-secondary-action" :href="downloadStudentArchiveFileUrl(file)">
            <el-icon><Download /></el-icon>下载原文件
          </a>
          <el-button v-if="file.can_delete" size="small" plain type="danger" @click="$emit('delete', file)">删除</el-button>
        </div>
      </article>
    </div>
    <div v-else class="empty-note">暂无归档资料。</div>
  </section>
</template>

<script setup lang="ts">
import { Document, Download, Files, PictureFilled, View } from '@element-plus/icons-vue'
import {
  downloadStudentArchiveFileUrl,
  previewStudentArchiveFileUrl,
  type StudentArchiveFile,
} from '../../../api/students'

defineProps<{ files: StudentArchiveFile[] }>()
defineEmits<{ delete: [file: StudentArchiveFile] }>()

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function archiveFilename(file: StudentArchiveFile) {
  return (file.original_filename || file.file || file.title).toLowerCase()
}

function archiveKind(file: StudentArchiveFile) {
  const filename = archiveFilename(file)
  if (filename.endsWith('.pdf')) return 'pdf'
  if (filename.endsWith('.doc') || filename.endsWith('.docx')) return 'word'
  if (filename.endsWith('.ppt') || filename.endsWith('.pptx')) return 'ppt'
  if (filename.endsWith('.png') || filename.endsWith('.jpg') || filename.endsWith('.jpeg')) return 'image'
  return 'file'
}

function archiveTypeLabel(file: StudentArchiveFile) {
  return ({ pdf: 'PDF', word: 'Word', ppt: 'PPT', image: '图片', file: '文件' } as Record<string, string>)[archiveKind(file)]
}

function archiveFileSizeLabel(file: StudentArchiveFile) {
  return file.file_size ? formatFileSize(file.file_size) : '大小未知'
}

function archivePreviewLabel(file: StudentArchiveFile) {
  const kind = archiveKind(file)
  if (kind === 'pdf' || kind === 'word' || kind === 'ppt') return '在线查看'
  if (kind === 'image') return '查看图片'
  return '查看文件'
}

function canPreviewArchive(file: StudentArchiveFile) {
  const kind = archiveKind(file)
  if (kind === 'word' || kind === 'ppt') return file.preview_status === 'ready'
  return true
}

function archivePreviewStatus(file: StudentArchiveFile) {
  if (file.preview_status === 'pending') return '正在生成预览'
  if (file.preview_status === 'failed') return '预览生成失败'
  if (archiveKind(file) === 'ppt' || archiveKind(file) === 'word') return '暂无在线预览'
  return '不可查看'
}

function archiveIcon(file: StudentArchiveFile) {
  const kind = archiveKind(file)
  if (kind === 'ppt') return Files
  if (kind === 'image') return PictureFilled
  return Document
}
</script>

<style scoped>
.files-panel {
  padding: 16px;
}

.files-panel:hover {
  transform: none;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.panel-heading p {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

.file-grid {
  display: grid;
  gap: 8px;
}

.file-card {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 9px 10px;
  background: var(--color-panel);
}

.file-card:hover {
  border-color: rgba(0, 135, 60, 0.18);
  background: #fff;
}

.file-icon {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-academic-blue);
}

.file-icon.pdf { background: #fff5f5; color: #9f312f; }
.file-icon.word { background: #eff6ff; color: #315f8f; }
.file-icon.ppt { background: #fff7ed; color: #a65f2b; }
.file-icon.image { background: var(--color-eco-green); color: var(--color-cau-green); }

.file-main {
  min-width: 0;
}

.file-title-row,
.file-meta,
.file-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-title-row strong {
  min-width: 0;
  overflow: hidden;
  color: var(--color-deep-green);
  font-size: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-title-row span,
.file-meta,
.file-preview-note {
  color: var(--color-muted);
  font-size: 12px;
}

.file-main p {
  overflow: hidden;
  margin: 3px 0 0;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-actions {
  justify-content: flex-end;
  white-space: nowrap;
}

.file-actions a {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.file-secondary-action {
  color: var(--color-muted) !important;
}

.empty-note {
  padding: 16px 4px;
  color: var(--color-muted);
  text-align: center;
}

@media (max-width: 760px) {
  .file-card {
    grid-template-columns: 34px minmax(0, 1fr);
  }

  .file-actions {
    grid-column: 1 / -1;
    flex-wrap: wrap;
    justify-content: flex-start;
  }
}
</style>
