<template>
  <section class="editor-grid">
    <CmsImportStrip
      description="批量导入专利成果，优先按专利号更新；没有专利号时按专利名称匹配。"
      template-url="/templates/patents-import-template.xlsx" :loading="importing" :progress="importProgress"
      uploading-text="正在上传专利成果表，请不要关闭页面。" processing-text="上传完成，正在写入专利成果。"
      @import="emit('import', $event)"
    />
    <CmsContentList title="专利成果" action-label="新增专利" :items="rows" :active-key="editingId || ''" @create="resetPatent" @edit="editPatent" />
    <article class="card form-panel">
      <div class="form-heading"><div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '专利成果' }}</h2></div></div>
      <el-form label-position="top">
        <el-form-item label="专利名称"><el-input v-model="form.title" /></el-form-item>
        <div class="form-two-col"><el-form-item label="专利号"><el-input v-model="form.patent_number" /></el-form-item><el-form-item label="状态"><el-input v-model="form.status" /></el-form-item></div>
        <el-form-item label="发明人"><el-input v-model="form.inventors" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="PDF 附件">
          <UploadFileField v-model="form.pdf_file" :disabled="saving" accept="application/pdf,.pdf" :max-size-mb="200" :existing-label="currentPdf ? displayFileLabel(currentPdf) : ''" />
        </el-form-item>
        <div class="form-two-col"><el-form-item label="申请日期"><el-date-picker v-model="form.application_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item><el-form-item label="授权日期"><el-date-picker v-model="form.authorization_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item></div>
        <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
        <el-form-item label="首页排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="savePatent" @delete="deletePatent" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi } from '../../../api/cms'
import type { Patent } from '../../../api/publicPortal'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import CmsImportStrip from './CmsImportStrip.vue'
import UploadFileField from '../../../components/UploadFileField.vue'
import type { CmsListRow } from '../composables/useCmsContentData'
import { useCmsEditorMutation } from '../composables/useCmsEditorMutation'

defineProps<{ rows: CmsListRow<Patent>[]; importing: boolean; importProgress: number; displayFileLabel: (value: string) => string }>()
const emit = defineEmits<{ import: [file: File]; changed: [] }>()

type PatentForm = Record<string, unknown> & {
  title: string
  patent_number: string
  inventors: string
  application_date: string
  authorization_date: string
  status: string
  pdf_file?: File
  visibility: string
  sort_order: number
}
const editingId = ref<number | null>(null)
const currentPdf = ref('')
const form = reactive<PatentForm>({ title: '', patent_number: '', inventors: '', application_date: '', authorization_date: '', status: '', pdf_file: undefined, visibility: 'public', sort_order: 0 })
const { saving, progress, save, remove } = useCmsEditorMutation(async () => emit('changed'))

function resetPatent() {
  editingId.value = null
  currentPdf.value = ''
  Object.assign(form, { title: '', patent_number: '', inventors: '', application_date: '', authorization_date: '', status: '', pdf_file: undefined, visibility: 'public', sort_order: 0 })
}

function editPatent(item: Patent) {
  editingId.value = item.id
  currentPdf.value = item.pdf_file || ''
  Object.assign(form, {
    title: item.title,
    patent_number: item.patent_number || '',
    inventors: item.inventors || '',
    application_date: item.application_date || '',
    authorization_date: item.authorization_date || '',
    status: item.status || '',
    pdf_file: undefined,
    visibility: item.visibility || 'public',
    sort_order: item.sort_order || 0,
  })
}

async function savePatent() {
  if (!form.title.trim()) {
    ElMessage.warning('请填写专利名称。')
    return
  }
  const id = editingId.value
  const succeeded = await save((onUploadProgress) =>
    id ? cmsApi.updatePatent(id, form, onUploadProgress) : cmsApi.createPatent(form, onUploadProgress),
  )
  if (succeeded) resetPatent()
}

async function deletePatent() {
  const id = editingId.value
  if (!id) return
  const succeeded = await remove('确定删除这个专利成果吗？', () => cmsApi.deletePatent(id))
  if (succeeded) resetPatent()
}
</script>
