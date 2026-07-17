<template>
  <section class="editor-grid">
    <CmsContentList title="研究方向" action-label="新增方向" :items="rows" :active-key="editingSlug" @create="resetResearch" @edit="editResearch" />
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
          <ImageCropField v-model="form.cover_image" :disabled="saving" :existing-url="currentCover" :existing-size="currentCoverSize" :aspect-ratio="4 / 3" :output-width="1600" :output-height="1200" :max-size-mb="20" />
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingSlug)" @save="saveResearch" @delete="deleteResearch" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi } from '../../../api/cms'
import type { ResearchDirection } from '../../../api/publicPortal'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import ImageCropField from '../../../components/ImageCropField.vue'
import type { CmsListRow } from '../composables/useCmsContentData'
import { useCmsEditorMutation } from '../composables/useCmsEditorMutation'

defineProps<{ rows: CmsListRow<ResearchDirection>[] }>()

const emit = defineEmits<{ changed: [] }>()
const editingSlug = ref('')
const currentCover = ref('')
const currentCoverSize = ref(0)
type ResearchForm = Record<string, unknown> & {
  title: string
  summary: string
  content: string
  cover_image?: File
  sort_order: number
}
const form = reactive<ResearchForm>({ title: '', summary: '', content: '', cover_image: undefined, sort_order: 0 })
const { saving, progress, save, remove } = useCmsEditorMutation(async () => emit('changed'))

function resetResearch() {
  editingSlug.value = ''
  currentCover.value = ''
  currentCoverSize.value = 0
  Object.assign(form, { title: '', summary: '', content: '', cover_image: undefined, sort_order: 0 })
}

function editResearch(item: ResearchDirection) {
  editingSlug.value = item.slug
  currentCover.value = item.cover_image || ''
  currentCoverSize.value = item.cover_image_size || 0
  Object.assign(form, {
    title: item.title,
    summary: item.summary,
    content: item.content || '',
    cover_image: undefined,
    sort_order: item.sort_order || 0,
  })
}

async function saveResearch() {
  if (!String(form.title || '').trim()) {
    ElMessage.warning('请填写研究方向标题。')
    return
  }
  const slug = editingSlug.value
  const succeeded = await save((onUploadProgress) =>
    slug ? cmsApi.updateResearch(slug, form, onUploadProgress) : cmsApi.createResearch(form, onUploadProgress),
  )
  if (succeeded) resetResearch()
}

async function deleteResearch() {
  const slug = editingSlug.value
  if (!slug) return
  const succeeded = await remove('确定删除这个研究方向吗？', () => cmsApi.deleteResearch(slug))
  if (succeeded) resetResearch()
}
</script>
