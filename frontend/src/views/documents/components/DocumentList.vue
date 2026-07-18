<template>
  <div class="document-list">
    <div class="document-grid">
      <article
        v-for="document in documents"
        :key="document.id"
        :class="['card document-card', { previewable: document.can_preview }]"
        @click="$emit('preview', document)"
      >
        <CompactDataRow :title="document.title" :description="document.description || '暂无资料说明。'">
          <template #leading><span class="file-type">{{ fileTypeLabel(document) }}</span></template>
          <template #meta>
            <dl>
              <div><dt>分类</dt><dd>{{ categoryName(document.category) }}</dd></div>
              <div><dt>大小</dt><dd>{{ currentFileSizeLabel(document) }}</dd></div>
              <div><dt>更新</dt><dd>{{ formatDate(document.updated_at) }}</dd></div>
            </dl>
          </template>
          <template #trailing>
            <div class="document-actions">
              <el-button v-if="document.can_edit" plain @click.stop="$emit('edit', document)">编辑</el-button>
              <el-button plain :disabled="!document.can_download" @click.stop="$emit('download', document)">
                {{ document.can_download ? '下载' : '不可下载' }}
              </el-button>
            </div>
          </template>
        </CompactDataRow>
      </article>
    </div>
    <AppPagination :page="page" :total-pages="totalPages" @change="$emit('update:page', $event)" />
  </div>
</template>

<script setup lang="ts">
import AppPagination from '../../../components/AppPagination.vue'
import CompactDataRow from '../../../components/CompactDataRow.vue'
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
  min-width: 0;
  padding: 0 16px;
  border-left: 3px solid transparent;
  box-shadow: none;
}

.document-card.previewable {
  cursor: pointer;
}

.document-card.previewable:hover {
  border-left-color: var(--color-cau-gold);
  border-color: var(--color-border-accent);
  box-shadow: var(--shadow-hover);
}

.file-type {
  border: 1px solid var(--color-line);
  border-left: 2px solid var(--color-cau-green);
  border-radius: 3px;
  padding: 3px 9px;
  background: var(--color-panel);
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 700;
}

.document-card dl {
  display: flex;
  flex-wrap: wrap;
  gap: 3px 18px;
  margin: 2px 0 0;
}

.document-card dl div {
  display: inline-flex;
  gap: 5px;
  color: var(--color-muted);
  font-size: 12px;
}

.document-card dt {
  color: var(--color-text);
}

.document-card dd {
  margin: 0;
}

.document-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 640px) {
  .document-card {
    padding: 0 12px;
  }

  .document-card dl {
    gap: 2px 12px;
  }

  .document-card dl div {
    display: inline-flex;
  }

  .document-card dd {
    max-width: 128px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .document-actions { width: 100%; }
  .document-actions :deep(.el-button) { flex: 1 1 120px; margin: 0; }
}
</style>
