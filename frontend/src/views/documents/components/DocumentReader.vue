<template>
  <section class="card embedded-reader">
    <header class="reader-heading">
      <div>
        <h2>{{ document.title }}</h2>
        <p>{{ currentFileLabel(document) }}</p>
      </div>
      <div class="reader-actions">
        <el-button plain @click="$emit('close')">返回列表</el-button>
        <el-button v-if="document.can_edit" plain @click="$emit('edit', document)">编辑</el-button>
        <el-button v-if="document.can_delete" plain type="danger" @click="$emit('delete', document)">删除</el-button>
        <el-button v-if="document.can_download" type="primary" @click="$emit('download', document)">下载</el-button>
      </div>
    </header>
    <dl class="reader-meta">
      <div><dt>分类</dt><dd>{{ categoryName(document.category) }}</dd></div>
      <div><dt>上传人</dt><dd>{{ document.uploaded_by_name || '组内成员' }}</dd></div>
      <div><dt>更新</dt><dd>{{ formatDate(document.updated_at) }}</dd></div>
      <div v-if="document.description"><dt>说明</dt><dd>{{ document.description }}</dd></div>
    </dl>
    <ExternalVideoCard
      v-if="document.external_url"
      class="reader-video"
      :url="document.external_url"
      :title="document.title"
    />
    <FilePreview
      v-else
      :url="canEmbed ? previewUrl : ''"
      :title="document.title"
      :filename="document.original_filename"
      :mime-type="document.file_type"
      :status="document.preview_status"
      :error="document.preview_error"
    >
      <template #fallback>
        <el-button v-if="document.can_download" type="primary" @click="$emit('download', document)">下载文件</el-button>
      </template>
    </FilePreview>
  </section>
</template>

<script setup lang="ts">
import type { LabDocument } from '../../../api/documents'
import FilePreview from '../../../components/FilePreview.vue'
import ExternalVideoCard from '../../../components/ExternalVideoCard.vue'
import { categoryName, currentFileLabel, formatDate } from '../documentPresentation'

defineProps<{ document: LabDocument; previewUrl: string; canEmbed: boolean }>()
defineEmits<{
  close: []
  edit: [document: LabDocument]
  delete: [document: LabDocument]
  download: [document: LabDocument]
}>()
</script>

<style scoped>
.embedded-reader {
  padding: 22px;
  box-shadow: 0 1px 2px rgba(31, 61, 43, 0.035), 0 12px 30px rgba(31, 61, 43, 0.035);
}

.embedded-reader:hover {
  border-color: var(--color-border);
  transform: none;
}

.reader-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
}

.reader-actions {
  display: flex;
  flex: 0 0 auto;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.reader-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 20px;
  font-weight: 650;
  line-height: 1.35;
}

.reader-heading p {
  overflow: hidden;
  max-width: min(720px, 58vw);
  margin: 4px 0 0;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reader-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  margin: 9px 0 0;
  color: var(--color-muted);
}

.reader-meta div {
  position: relative;
  padding: 3px 12px 3px 0;
}

.reader-meta div + div { padding-left: 12px; }
.reader-meta div + div::before { position: absolute; top: 8px; left: 0; width: 3px; height: 3px; border-radius: 50%; background: var(--color-border); content: ''; }
.reader-meta div:last-child { flex-basis: 100%; padding-left: 0; }
.reader-meta div:last-child::before { display: none; }

.reader-meta dt,
.reader-meta dd {
  display: inline;
  margin: 0;
  font-size: 12px;
}

.reader-meta dt {
  color: var(--color-muted);
}

.reader-meta dd {
  margin-left: 5px;
  color: var(--color-text);
  font-weight: 650;
}

.embedded-reader :deep(.file-preview) { margin-top: 9px; }
.reader-video { margin-top: 12px; }

@media (max-width: 640px) {
  .reader-heading {
    display: grid;
  }

  .reader-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    justify-content: stretch;
  }

  .reader-actions :deep(.el-button) { width: 100%; margin: 0; }

  .reader-heading p {
    max-width: 100%;
  }
}
</style>
