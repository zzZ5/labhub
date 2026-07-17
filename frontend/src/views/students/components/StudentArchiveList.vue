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
      <FileInfoRow
        v-for="file in files" :key="file.id" :title="file.title" :filename="file.original_filename"
        :size="file.file_size" :description="file.description || file.file_type_label" :uploaded-at="file.uploaded_at"
        :status="archivePreviewStatusLabel(file)"
      >
        <template #actions>
          <a v-if="canPreviewArchive(file)" class="file-primary-action" :href="previewStudentArchiveFileUrl(file)" target="_blank" rel="noreferrer">
            <el-icon><View /></el-icon>{{ archivePreviewLabel(file) }}
          </a>
          <span v-else class="file-preview-note">{{ archivePreviewStatus(file) }}</span>
          <a class="file-secondary-action" :href="downloadStudentArchiveFileUrl(file)">
            <el-icon><Download /></el-icon>下载原文件
          </a>
          <ActionMenu v-if="file.can_delete" :items="deleteItems" @command="$emit('delete', file)" />
        </template>
      </FileInfoRow>
    </div>
    <div v-else class="empty-note">暂无归档资料。</div>
  </section>
</template>

<script setup lang="ts">
import { Download, View } from '@element-plus/icons-vue'
import FileInfoRow from '../../../components/FileInfoRow.vue'
import ActionMenu, { type ActionMenuItem } from '../../../components/ActionMenu.vue'
import {
  downloadStudentArchiveFileUrl,
  previewStudentArchiveFileUrl,
  type StudentArchiveFile,
} from '../../../api/students'

defineProps<{ files: StudentArchiveFile[] }>()
defineEmits<{ delete: [file: StudentArchiveFile] }>()
const deleteItems: ActionMenuItem[] = [{ command: 'delete', label: '删除资料', danger: true }]

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

function archivePreviewStatusLabel(file: StudentArchiveFile) {
  if (file.preview_status === 'pending') return '预览处理中'
  if (file.preview_status === 'failed') return '预览失败'
  if (file.preview_status === 'ready') return '可在线查看'
  return file.file_type_label || ''
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

.file-preview-note {
  color: var(--color-muted);
  font-size: 12px;
}

.file-grid :deep(a) {
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

</style>
