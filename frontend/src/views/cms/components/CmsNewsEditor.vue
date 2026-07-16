<template>
  <section class="editor-grid news-editor-grid">
    <CmsContentList title="新闻活动" action-label="新增新闻" :items="rows" :active-key="editingSlug" @create="$emit('create')" @edit="$emit('edit', $event)" />
    <article class="card form-panel news-form-panel">
      <div class="form-heading"><div><span>{{ editingSlug ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '新闻活动' }}</h2></div></div>
      <el-form label-position="top">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <div class="form-two-col"><el-form-item label="活动日期"><el-date-picker v-model="form.event_date" type="date" value-format="YYYY-MM-DD" /></el-form-item><el-form-item label="地点"><el-input v-model="form.location" /></el-form-item></div>
        <div class="form-two-col">
          <el-form-item label="分类"><el-select v-model="form.category_id" clearable placeholder="选择分类"><el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" /></el-select></el-form-item>
          <el-form-item label="状态"><el-select v-model="form.status"><el-option label="草稿" value="draft" /><el-option label="发布" value="published" /><el-option label="归档" value="archived" /></el-select></el-form-item>
        </div>
        <el-form-item label="摘要"><el-input v-model="form.summary" type="textarea" :rows="2" maxlength="260" show-word-limit /></el-form-item>
        <el-form-item label="正文" class="news-body-field">
          <RichTextEditor ref="editorRef" :model-value="content" :uploading="uploadingImage" :upload-progress="imageUploadProgress" @update:model-value="$emit('update:content', $event)" @image-selected="$emit('imageSelected', $event)" />
          <small>插图会放在当前光标位置。上传 Word 后保存，内容会转入这里并可继续编辑。</small>
        </el-form-item>
        <div class="news-assets-grid">
          <div class="news-asset-field">
            <strong>Word 稿件</strong>
            <input :key="fileInputKey" class="file-input" type="file" accept=".docx" @change="$emit('wordFile', $event)" />
            <small v-if="selectedWordFile">{{ selectedWordFile.name }}（{{ formatFileSize(selectedWordFile.size) }}）</small>
            <small v-else-if="currentWordFile">已上传：{{ displayFileLabel(currentWordFile) }}</small>
            <small v-else>可选，支持 .docx 正文和内嵌图片。</small>
          </div>
          <div class="news-asset-field">
            <strong>封面图</strong>
            <input class="file-input" type="file" accept="image/*" @change="$emit('coverFile', $event)" />
            <small v-if="currentCover">已上传：{{ displayFileLabel(currentCover) }}</small>
            <small v-else>用于新闻列表，未上传时使用正文首图。</small>
          </div>
        </div>
        <div v-if="uploadProgress > 0 || saving" class="upload-progress news-save-progress">
          <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
          <span>{{ uploadProgress < 100 ? '正在上传并保存…' : '上传完成，正在处理正文。' }}</span>
        </div>
        <div class="form-two-col">
          <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
          <el-form-item label="置顶"><el-switch v-model="form.is_pinned" /></el-form-item>
        </div>
      </el-form>
      <CmsFormActions :saving="saving" :deletable="Boolean(editingSlug)" @save="$emit('save')" @delete="$emit('delete')" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import RichTextEditor from '../../../components/RichTextEditor.vue'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'

defineProps<{
  rows: Array<any>; editingSlug: string; form: Record<string, any>; categories: Array<any>; content: string
  uploadingImage: boolean; imageUploadProgress: number; fileInputKey: number; selectedWordFile: File | null
  currentWordFile: string; currentCover: string; uploadProgress: number; saving: boolean
  displayFileLabel: (value: string) => string; formatFileSize: (size: number) => string
}>()
defineEmits<{
  create: []; edit: [row: any]; save: []; delete: []; 'update:content': [value: string]
  imageSelected: [file: File]; wordFile: [event: Event]; coverFile: [event: Event]
}>()

const editorRef = ref<{ insertImage: (src: string, alt?: string) => void } | null>(null)
defineExpose({ insertImage: (src: string, alt?: string) => editorRef.value?.insertImage(src, alt) })
</script>
