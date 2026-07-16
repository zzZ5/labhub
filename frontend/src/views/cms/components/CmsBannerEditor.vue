<template>
  <section class="editor-grid">
    <CmsContentList title="首页横幅" action-label="新增横幅" :items="rows" :active-key="editingId || ''" @create="$emit('create')" @edit="$emit('edit', $event)" />
    <article class="card form-panel">
      <div class="form-heading">
        <div>
          <span>{{ editingId ? '正在编辑' : '新增内容' }}</span>
          <h2>{{ form.title || '首页横幅' }}</h2>
          <p>标题和副标题会显示在对应图片上；留空时首页使用站点名称和副标题。</p>
        </div>
      </div>
      <div v-if="defaultHero" class="legacy-banner-note">
        <img :src="defaultHero" alt="默认横幅预览" />
        <div>
          <strong>默认横幅</strong>
          <span>{{ siteForm.site_name || '中农雨磷' }}</span>
          <small v-if="siteForm.keywords">{{ siteForm.keywords }}</small>
          <small>{{ displayFileLabel(defaultHero) }}</small>
          <small>没有轮播横幅时首页使用此图；新增横幅后优先展示列表中的横幅。</small>
        </div>
      </div>
      <el-form label-position="top">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="副标题"><el-input v-model="form.subtitle" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="横幅图片">
          <ImageCropField v-model="form.image" :disabled="saving" :existing-url="currentImage" :aspect-ratio="12 / 5" :output-width="1920" :output-height="800" :max-size-mb="20" hint="按首页横幅比例裁剪，主体尽量居中" />
        </el-form-item>
        <el-form-item label="跳转链接"><el-input v-model="form.link" placeholder="可选，https://..." /></el-form-item>
        <div class="form-two-col">
          <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
        </div>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="$emit('save')" @delete="$emit('delete')" />
    </article>
  </section>
</template>

<script setup lang="ts">
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import ImageCropField from '../../../components/ImageCropField.vue'

defineProps<{
  rows: Array<any>
  editingId: number | null
  form: Record<string, any>
  siteForm: Record<string, any>
  defaultHero: string
  currentImage: string
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
