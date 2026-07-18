<template>
  <section class="editor-grid" :class="{ 'mobile-editor-open': mobileEditorOpen }">
    <CmsContentList title="科研项目" action-label="新增项目" :items="rows" :active-key="editingId || ''" @create="createProject" @edit="openProject">
      <template #tools><CmsImportStrip description="批量导入科研项目，优先按项目编号更新；没有编号时按项目名称匹配。" template-url="/templates/projects-import-template.xlsx" :loading="importing" :progress="importProgress" :completed="importCompleted" uploading-text="正在上传科研项目表，请不要关闭页面。" processing-text="上传完成，正在写入科研项目。" @import="emit('import', $event)" @reset="emit('resetImport')" /></template>
    </CmsContentList>
    <article class="card form-panel">
      <CmsMobileEditorBack @back="mobileEditorOpen = false" />
      <div class="form-heading"><div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '科研项目' }}</h2></div></div>
      <el-form label-position="top">
        <div class="form-section-label"><strong>基础信息</strong><span>项目名称、编号和来源</span></div>
        <el-form-item label="项目名称"><el-input v-model="form.title" /></el-form-item>
        <div class="form-two-col">
          <el-form-item label="项目编号"><el-input v-model="form.project_number" /></el-form-item>
          <el-form-item label="资助来源"><el-input v-model="form.funding_source" /></el-form-item>
        </div>
        <div class="form-two-col">
          <el-form-item label="负责人"><el-input v-model="form.principal_investigator" /></el-form-item>
          <el-form-item label="状态"><el-input v-model="form.status" /></el-form-item>
        </div>
        <div class="form-two-col">
          <el-form-item label="经费"><el-input v-model="form.amount" placeholder="可留空" /></el-form-item>
          <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
        </div>
        <div class="form-two-col">
          <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
          <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
        </div>
        <div class="form-section-label"><strong>项目说明</strong><span>公开展示的简要内容</span></div>
        <el-form-item label="说明"><el-input v-model="form.description" type="textarea" :rows="4" /></el-form-item>
        <div class="form-section-label"><strong>展示设置</strong><span>控制首页展示顺序</span></div>
        <el-form-item label="首页排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="saveProject" @delete="deleteProject" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi } from '../../../api/cms'
import type { Project } from '../../../api/publicPortal'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import CmsImportStrip from './CmsImportStrip.vue'
import CmsMobileEditorBack from './CmsMobileEditorBack.vue'
import type { CmsListRow } from '../composables/useCmsContentData'
import { useCmsEditorMutation } from '../composables/useCmsEditorMutation'

defineProps<{ rows: CmsListRow<Project>[]; importing: boolean; importProgress: number; importCompleted: boolean }>()
const emit = defineEmits<{ import: [file: File]; changed: []; resetImport: [] }>()

type ProjectForm = Record<string, unknown> & {
  title: string
  project_number: string
  funding_source: string
  principal_investigator: string
  start_date: string
  end_date: string
  amount: string | number
  status: string
  visibility: string
  description: string
  sort_order: number
}
const editingId = ref<number | null>(null)
const mobileEditorOpen = ref(false)
const form = reactive<ProjectForm>({
  title: '', project_number: '', funding_source: '', principal_investigator: '', start_date: '', end_date: '',
  amount: '', status: '', visibility: 'public', description: '', sort_order: 0,
})
const { saving, progress, save, remove } = useCmsEditorMutation(async () => emit('changed'))

function resetProject() {
  editingId.value = null
  Object.assign(form, {
    title: '', project_number: '', funding_source: '', principal_investigator: '', start_date: '', end_date: '',
    amount: '', status: '', visibility: 'public', description: '', sort_order: 0,
  })
}

function createProject() {
  resetProject()
  mobileEditorOpen.value = true
}

function openProject(item: Project) {
  editProject(item)
  mobileEditorOpen.value = true
}

function editProject(item: Project) {
  editingId.value = item.id
  Object.assign(form, {
    title: item.title,
    project_number: item.project_number || '',
    funding_source: item.funding_source || '',
    principal_investigator: item.principal_investigator || '',
    start_date: item.start_date || '',
    end_date: item.end_date || '',
    amount: item.amount || '',
    status: item.status || '',
    visibility: item.visibility || 'public',
    description: item.description || '',
    sort_order: item.sort_order || 0,
  })
}

async function saveProject() {
  if (!form.title.trim()) {
    ElMessage.warning('请填写项目名称。')
    return
  }
  const id = editingId.value
  const succeeded = await save((onUploadProgress) =>
    id ? cmsApi.updateProject(id, form, onUploadProgress) : cmsApi.createProject(form, onUploadProgress),
  )
  if (succeeded) {
    resetProject()
    mobileEditorOpen.value = false
  }
}

async function deleteProject() {
  const id = editingId.value
  if (!id) return
  const succeeded = await remove('确定删除这个科研项目吗？', () => cmsApi.deleteProject(id))
  if (succeeded) {
    resetProject()
    mobileEditorOpen.value = false
  }
}
</script>
