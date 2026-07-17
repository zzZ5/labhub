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
            <el-button plain :disabled="!document.can_download" @click.stop="$emit('download', document)">
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
  gap: 10px;
}

.document-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) 170px auto;
  align-items: center;
  min-height: 108px;
  gap: 14px;
  padding: 14px 16px;
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
  align-self: start;
  margin: 2px 0 0;
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
  margin: 0 0 4px;
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 650;
  line-height: 1.35;
}

.document-card p {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.document-card dl {
  display: grid;
  gap: 4px;
  margin: 0;
  border-left: 1px solid var(--color-line);
  padding-left: 14px;
}

.document-card dl div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  color: var(--color-muted);
  font-size: 12px;
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
  margin: 0;
}

.preview-hint {
  display: none;
}

.document-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 640px) {
  .document-card {
    grid-template-columns: auto minmax(0, 1fr);
    min-height: 0;
    gap: 8px 10px;
    padding: 13px;
  }

  .document-card dl,
  .document-card footer {
    grid-column: 1 / -1;
  }

  .document-card dl {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    border-top: 1px solid var(--color-line);
    border-left: 0;
    padding: 9px 0 0;
  }

  .document-card dl div {
    display: grid;
    gap: 2px;
  }

  .document-card dd {
    overflow: hidden;
    text-align: left;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .document-card footer {
    display: flex;
    border-top: 0;
    padding-top: 0;
  }
}
</style>
