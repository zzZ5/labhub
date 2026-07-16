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
    <div class="document-reader">
      <iframe v-if="previewUrl && canEmbed" :src="previewUrl" title="资料在线查看" />
      <div v-else class="preview-empty">
        <strong>当前文件暂不能在线查看</strong>
        <p>请下载后查看，或将旧版 Word 文件转换为 PDF / DOCX 后重新上传。</p>
        <el-button v-if="document.can_download" type="primary" @click="$emit('download', document)">下载文件</el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { LabDocument } from '../../../api/documents'
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
  gap: 7px;
  margin: 10px 0 0;
}

.reader-meta div {
  border: 1px solid var(--color-line);
  border-radius: 999px;
  padding: 5px 10px;
  background: var(--color-panel);
}

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

.document-reader {
  overflow: hidden;
  border: 1px solid #dfe5e1;
  border-radius: 10px;
  margin-top: 10px;
  background: #eef2f0;
}

.document-reader iframe {
  display: block;
  width: 100%;
  min-height: min(86vh, 980px);
  border: 0;
  background: #fff;
}

.preview-empty {
  display: grid;
  min-height: 420px;
  place-items: center;
  align-content: center;
  gap: 10px;
  padding: 32px;
  color: var(--color-muted);
  text-align: center;
}

.preview-empty strong {
  color: var(--color-deep-green);
  font-size: 20px;
}

.preview-empty p {
  max-width: 460px;
  margin: 0;
}

@media (max-width: 640px) {
  .reader-heading {
    display: grid;
  }

  .reader-actions {
    justify-content: flex-start;
  }

  .reader-heading p {
    max-width: 100%;
  }
}
</style>
