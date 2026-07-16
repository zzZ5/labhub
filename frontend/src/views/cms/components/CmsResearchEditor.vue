<template>
  <section class="editor-grid">
    <CmsContentList title="研究方向" action-label="新增方向" :items="rows" :active-key="editingSlug" @create="$emit('create')" @edit="$emit('edit', $event)" />
    <article class="card form-panel">
      <div class="form-heading">
        <div>
          <span>{{ editingSlug ? '正在编辑' : '新增内容' }}</span>
          <h2>{{ form.title || '研究方向' }}</h2>
        </div>
      </div>
      <el-form label-position="top">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="摘要"><el-input v-model="form.summary" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="详细内容"><el-input v-model="form.content" type="textarea" :rows="5" /></el-form-item>
        <el-form-item label="封面图">
          <ImageCropField v-model="form.cover_image" :disabled="saving" :existing-url="currentCover" :aspect-ratio="4 / 3" :output-width="1600" :output-height="1200" :max-size-mb="20" />
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingSlug)" @save="$emit('save')" @delete="$emit('delete')" />
    </article>
  </section>
</template>

<script setup lang="ts">
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import ImageCropField from '../../../components/ImageCropField.vue'

defineProps<{
  rows: Array<any>
  editingSlug: string
  form: Record<string, any>
  currentCover: string
  saving: boolean
  progress: number
  displayFileLabel: (value: string) => string
}>()

defineEmits<{
  create: []
  edit: [row: any]
  save: []
  delete: []
}>()
</script>
