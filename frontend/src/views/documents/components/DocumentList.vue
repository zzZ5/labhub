<template>
  <div class="document-list">
    <div class="document-grid">
      <article
        v-for="document in documents"
        :key="document.id"
        :class="['card document-card', { previewable: document.can_preview }]"
        @click="$emit('preview', document)"
      >
        <div class="document-topline"><span class="file-type">{{ fileTypeLabel(document) }}</span></div>
        <div>
          <h3>{{ document.title }}</h3>
          <p>{{ document.description || '暂无资料说明。' }}</p>
        </div>
        <dl>
          <div><dt>分类</dt><dd>{{ categoryName(document.category) }}</dd></div>
          <div><dt>大小</dt><dd>{{ currentFileSizeLabel(document) }}</dd></div>
          <div><dt>更新</dt><dd>{{ formatDate(document.updated_at) }}</dd></div>
        </dl>
        <footer>
          <span class="preview-hint">{{ document.can_preview ? '点击卡片查看' : '暂无可预览文件' }}</span>
          <div class="document-actions">
            <el-button v-if="document.can_edit" plain @click.stop="$emit('edit', document)">编辑</el-button>
            <el-button type="primary" :disabled="!document.can_download" @click.stop="$emit('download', document)">
              {{ document.can_download ? '下载' : '不可下载' }}
            </el-button>
          </div>
        </footer>
      </article>
    </div>
    <AppPagination :page="page" :total-pages="totalPages" @change="$emit('update:page', $event)" />
  </div>
</template>

<script setup lang="ts">
import AppPagination from '../../../components/AppPagination.vue'
import type { LabDocument } from '../../../api/documents'
import { categoryName, currentFileSizeLabel, fileTypeLabel, formatDate } from '../documentPresentation'

defineProps<{
  documents: LabDocument[]
  total: number
  page: number
  totalPages: number
}>()

defineEmits<{
  preview: [document: LabDocument]
  edit: [document: LabDocument]
  download: [document: LabDocument]
  'update:page': [page: number]
}>()
</script>

<style scoped>
.document-list {
  display: grid;
  gap: 14px;
}

.document-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.document-card {
  display: flex;
  flex-direction: column;
  min-height: 286px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(31, 61, 43, 0.035);
}

.document-card.previewable {
  cursor: pointer;
}

.document-card.previewable:hover {
  border-color: rgba(0, 135, 60, 0.24);
  box-shadow: 0 12px 26px rgba(31, 61, 43, 0.055);
}

.document-card.previewable:hover h3 {
  color: var(--color-cau-green);
}

.document-topline {
  margin-bottom: 16px;
}

.file-type {
  border: 1px solid var(--color-line);
  border-radius: 999px;
  padding: 3px 9px;
  background: var(--color-panel);
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 700;
}

.document-card h3 {
  margin: 0 0 10px;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
  line-height: 1.35;
}

.document-card p {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: var(--color-muted);
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.document-card dl {
  display: grid;
  gap: 8px;
  margin: 18px 0;
  border-top: 1px solid var(--color-line);
  padding-top: 14px;
}

.document-card dl div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  color: var(--color-muted);
  font-size: 14px;
}

.document-card dt {
  color: var(--color-text);
}

.document-card dd {
  margin: 0;
  text-align: right;
}

.document-card footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: auto;
}

.preview-hint {
  color: var(--color-muted);
  font-size: 13px;
}

.document-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 640px) {
  .document-card footer {
    display: grid;
  }

}
</style>
