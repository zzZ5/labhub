<template>
  <section class="editor-grid news-editor-grid">
    <CmsContentList title="新闻活动" action-label="新增新闻" :items="rows" :active-key="editingSlug" @create="resetNews" @edit="editNews" />
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
          <RichTextEditor ref="editorRef" :model-value="form.content" :uploading="uploadingImage" :upload-progress="imageUploadProgress" @update:model-value="form.content = $event" @image-selected="insertNewsBodyImage" />
          <small>插图会放在当前光标位置。上传 Word 后保存，内容会转入这里并可继续编辑。</small>
        </el-form-item>
        <div class="news-assets-grid">
          <div class="news-asset-field">
            <strong>Word 稿件</strong>
            <UploadFileField v-model="form.word_file" :disabled="saving" accept=".docx" :max-size-mb="200" :existing-label="currentWordFile ? displayFileLabel(currentWordFile) : ''" hint="可选，支持 .docx 正文和内嵌图片，文件不超过 200 MB" />
          </div>
          <div class="news-asset-field">
            <strong>封面图</strong>
            <ImageCropField v-model="form.cover_image" :disabled="saving" :existing-url="currentCover" :existing-size="currentCoverSize" :aspect-ratio="32 / 17" :output-width="1600" :output-height="850" :max-size-mb="20" hint="用于新闻列表；未上传时使用正文首图" />
          </div>
        </div>
        <UploadProgress :active="saving" :progress="progress" uploading-text="正在上传并保存…" processing-text="上传完成，正在处理正文。" />
        <div class="form-two-col">
          <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
          <el-form-item label="置顶"><el-switch v-model="form.is_pinned" /></el-form-item>
        </div>
      </el-form>
      <CmsFormActions :saving="saving" :deletable="Boolean(editingSlug)" @save="saveNews" @delete="deleteNews" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi, type CmsNewsArticle } from '../../../api/cms'
import type { NewsCategory } from '../../../api/publicPortal'
import { UPLOAD_LIMIT, validateUploadFile } from '../../../utils/files'
import RichTextEditor from '../../../components/RichTextEditor.vue'
import UploadFileField from '../../../components/UploadFileField.vue'
import ImageCropField from '../../../components/ImageCropField.vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import type { CmsListRow } from '../composables/useCmsContentData'
import { useCmsEditorMutation } from '../composables/useCmsEditorMutation'

defineProps<{
  rows: CmsListRow<CmsNewsArticle>[]
  categories: NewsCategory[]
  displayFileLabel: (value: string) => string
}>()
const emit = defineEmits<{ changed: [] }>()

const editorRef = ref<{ insertImage: (src: string, alt?: string) => void } | null>(null)
const editingSlug = ref('')
const editingId = ref<number | null>(null)
const currentWordFile = ref('')
const currentCover = ref('')
const currentCoverSize = ref(0)
const uploadingImage = ref(false)
const imageUploadProgress = ref(0)

type NewsForm = Record<string, unknown> & {
  title: string
  summary: string
  content: string
  cover_image?: File
  word_file?: File
  event_date: string
  location: string
  category_id: number | null
  status: string
  visibility: string
  is_pinned: boolean
}
const form = reactive<NewsForm>({
  title: '', summary: '', content: '', cover_image: undefined, word_file: undefined, event_date: '', location: '',
  category_id: null, status: 'published', visibility: 'public', is_pinned: false,
})
const { saving, progress, saveResult, remove, errorMessage } = useCmsEditorMutation(async () => emit('changed'))

function resetNews() {
  editingSlug.value = ''
  editingId.value = null
  currentCover.value = ''
  currentCoverSize.value = 0
  currentWordFile.value = ''
  imageUploadProgress.value = 0
  Object.assign(form, {
    title: '', summary: '', content: '', cover_image: undefined, word_file: undefined, event_date: '', location: '',
    category_id: null, status: 'published', visibility: 'public', is_pinned: false,
  })
}

function editNews(item: CmsNewsArticle) {
  editingSlug.value = item.slug
  editingId.value = item.id
  currentCover.value = item.cover_image || ''
  currentCoverSize.value = item.cover_image_size || 0
  currentWordFile.value = item.word_file || ''
  imageUploadProgress.value = 0
  Object.assign(form, {
    title: item.title,
    summary: item.summary || '',
    content: item.word_html || item.content || '',
    cover_image: undefined,
    word_file: undefined,
    event_date: item.event_date || '',
    location: item.location || '',
    category_id: item.category?.id || null,
    status: item.status || 'published',
    visibility: item.visibility || 'public',
    is_pinned: item.is_pinned || false,
  })
}

async function saveNews() {
  if (!form.title.trim()) {
    ElMessage.warning('请填写新闻标题。')
    return
  }
  const slug = editingSlug.value
  const outcome = await saveResult(
    (onUploadProgress) => slug ? cmsApi.updateNews(slug, form, onUploadProgress) : cmsApi.createNews(form, onUploadProgress),
    '新闻已保存',
  )
  if (outcome.succeeded && outcome.result) editNews(outcome.result)
}

async function deleteNews() {
  const slug = editingSlug.value
  if (!slug) return
  const succeeded = await remove('确定删除这条新闻吗？', () => cmsApi.deleteNews(slug))
  if (succeeded) resetNews()
}

async function ensureNewsDraft() {
  if (editingId.value) return editingId.value
  const title = form.title.trim()
  if (!title) {
    ElMessage.warning('请先填写新闻标题，再插入图片。')
    return null
  }
  const saved = await cmsApi.createNews({
    title,
    summary: form.summary,
    content: form.content,
    event_date: form.event_date,
    location: form.location,
    category_id: form.category_id,
    status: 'draft',
    visibility: form.visibility,
    is_pinned: false,
  })
  editingId.value = saved.id
  editingSlug.value = saved.slug
  form.status = 'draft'
  emit('changed')
  return saved.id
}

async function insertNewsBodyImage(file: File) {
  const validationMessage = validateUploadFile(file, UPLOAD_LIMIT.image)
  if (validationMessage) {
    ElMessage.warning(validationMessage)
    return
  }
  uploadingImage.value = true
  imageUploadProgress.value = 0
  try {
    const articleId = await ensureNewsDraft()
    if (!articleId) return
    const uploaded = await cmsApi.createNewsImage({ article_id: articleId, image: file, caption: '正文插图', sort_order: 0 }, (event) => {
      if (event.total) imageUploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    imageUploadProgress.value = 100
    editorRef.value?.insertImage(uploaded.image, file.name)
    ElMessage.success('图片已插入正文，请保存新闻。')
  } catch (error) {
    ElMessage.error(errorMessage(error, '图片上传失败。'))
  } finally {
    uploadingImage.value = false
    setTimeout(() => {
      if (!uploadingImage.value) imageUploadProgress.value = 0
    }, 800)
  }
}
</script>
