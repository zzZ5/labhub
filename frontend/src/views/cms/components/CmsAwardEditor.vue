<template>
  <section class="editor-grid" :class="{ 'mobile-editor-open': mobileEditorOpen }">
    <CmsContentList title="获奖成果" action-label="新增获奖" :items="rows" :active-key="editingId || ''" @create="createAward" @edit="openAward">
      <template #tools><CmsImportStrip description="批量导入获奖成果，按奖项名称和获奖日期更新；Excel 行内图片会作为获奖图片。" template-url="/templates/awards-import-template.xlsx" :loading="importing" :progress="importProgress" uploading-text="正在上传获奖成果表，请不要关闭页面。" processing-text="上传完成，正在写入获奖成果。" @import="emit('import', $event)" /></template>
    </CmsContentList>
    <article class="card form-panel">
      <CmsMobileEditorBack @back="mobileEditorOpen = false" />
      <div class="form-heading"><div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '获奖成果' }}</h2></div></div>
      <el-form label-position="top">
        <div class="form-section-label"><strong>基础信息</strong><span>奖项、日期和参与人员</span></div>
        <el-form-item label="奖项名称"><el-input v-model="form.title" /></el-form-item>
        <div class="form-two-col"><el-form-item label="奖项等级"><el-input v-model="form.award_level" /></el-form-item><el-form-item label="获奖日期"><el-date-picker v-model="form.award_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item></div>
        <el-form-item label="参与人员"><el-input v-model="form.participants" type="textarea" :rows="2" /></el-form-item>
        <div class="form-section-label"><strong>媒体与附件</strong><span>获奖图片和证明文件</span></div>
        <div class="form-two-col">
          <el-form-item label="获奖图片"><ImageCropField v-model="form.image" :disabled="saving" :existing-url="currentImage" :existing-size="currentImageSize" :aspect-ratio="4 / 3" :output-width="1600" :output-height="1200" :max-size-mb="20" /></el-form-item>
          <el-form-item label="附件"><UploadFileField v-model="form.attachment" :disabled="saving" accept="application/pdf,image/*,.pdf" :max-size-mb="200" :existing-label="currentAttachment ? displayFileLabel(currentAttachment) : ''" /></el-form-item>
        </div>
        <div class="form-section-label"><strong>说明与展示</strong><span>公开说明、权限和首页顺序</span></div>
        <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
        <el-form-item label="说明"><el-input v-model="form.description" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="首页排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="saveAward" @delete="deleteAward" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi } from '../../../api/cms'
import type { Award } from '../../../api/publicPortal'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import CmsImportStrip from './CmsImportStrip.vue'
import CmsMobileEditorBack from './CmsMobileEditorBack.vue'
import UploadFileField from '../../../components/UploadFileField.vue'
import ImageCropField from '../../../components/ImageCropField.vue'
import type { CmsListRow } from '../composables/useCmsContentData'
import { useCmsEditorMutation } from '../composables/useCmsEditorMutation'

defineProps<{ rows: CmsListRow<Award>[]; importing: boolean; importProgress: number; displayFileLabel: (value: string) => string }>()
const emit = defineEmits<{ import: [file: File]; changed: [] }>()

type AwardForm = Record<string, unknown> & {
  title: string
  award_level: string
  award_date: string
  participants: string
  description: string
  image?: File
  attachment?: File
  visibility: string
  sort_order: number
}
const editingId = ref<number | null>(null)
const mobileEditorOpen = ref(false)
const currentImage = ref('')
const currentImageSize = ref(0)
const currentAttachment = ref('')
const form = reactive<AwardForm>({ title: '', award_level: '', award_date: '', participants: '', description: '', image: undefined, attachment: undefined, visibility: 'public', sort_order: 0 })
const { saving, progress, save, remove } = useCmsEditorMutation(async () => emit('changed'))

function resetAward() {
  editingId.value = null
  currentImage.value = ''
  currentImageSize.value = 0
  currentAttachment.value = ''
  Object.assign(form, { title: '', award_level: '', award_date: '', participants: '', description: '', image: undefined, attachment: undefined, visibility: 'public', sort_order: 0 })
}

function createAward() {
  resetAward()
  mobileEditorOpen.value = true
}

function openAward(item: Award) {
  editAward(item)
  mobileEditorOpen.value = true
}

function editAward(item: Award) {
  editingId.value = item.id
  currentImage.value = item.image || ''
  currentImageSize.value = item.image_size || 0
  currentAttachment.value = item.attachment || ''
  Object.assign(form, {
    title: item.title,
    award_level: item.award_level || '',
    award_date: item.award_date || '',
    participants: item.participants || '',
    description: item.description || '',
    image: undefined,
    attachment: undefined,
    visibility: item.visibility || 'public',
    sort_order: item.sort_order || 0,
  })
}

async function saveAward() {
  if (!form.title.trim()) {
    ElMessage.warning('请填写奖项名称。')
    return
  }
  const id = editingId.value
  const succeeded = await save((onUploadProgress) =>
    id ? cmsApi.updateAward(id, form, onUploadProgress) : cmsApi.createAward(form, onUploadProgress),
  )
  if (succeeded) {
    resetAward()
    mobileEditorOpen.value = false
  }
}

async function deleteAward() {
  const id = editingId.value
  if (!id) return
  const succeeded = await remove('确定删除这个获奖成果吗？', () => cmsApi.deleteAward(id))
  if (succeeded) {
    resetAward()
    mobileEditorOpen.value = false
  }
}
</script>
