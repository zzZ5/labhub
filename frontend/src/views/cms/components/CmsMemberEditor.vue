<template>
  <section class="editor-grid">
    <CmsContentList title="团队成员" action-label="新增成员" :items="rows" :active-key="editingId || ''" @create="resetMember" @edit="editMember">
      <template #tools><CmsImportStrip description="批量导入团队成员，可填写姓名、身份头衔、研究方向、邮箱、简介和展示排序。" template-url="/templates/members-import-template.xlsx" :loading="importing" :progress="importProgress" uploading-text="正在上传团队成员表，请不要关闭页面。" processing-text="上传完成，正在写入团队成员。" @import="emit('import', $event)" /></template>
    </CmsContentList>
    <article class="card form-panel">
      <div class="form-heading">
        <div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.name || '团队成员' }}</h2></div>
      </div>
      <el-form label-position="top">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <div class="form-two-col">
          <el-form-item label="身份头衔"><el-input v-model="form.role_type" placeholder="如：副教授 / 博士生导师、博士研究生、硕士研究生" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        </div>
        <el-form-item label="研究方向"><el-input v-model="form.research_direction" /></el-form-item>
        <el-form-item label="头像">
          <ImageCropField v-model="form.avatar" :disabled="saving" :existing-url="currentAvatar" :existing-size="currentAvatarSize" :aspect-ratio="4 / 5" :output-width="800" :output-height="1000" :max-size-mb="10" hint="按团队成员照片比例裁剪，人物面部尽量居中" />
        </el-form-item>
        <el-form-item label="简介"><el-input v-model="form.profile" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="展示排序">
          <el-input-number v-model="form.sort_order" :min="0" />
          <small>0 表示不在公开网站展示；大于 0 时按数字从小到大排序。</small>
        </el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="saveMember" @delete="deleteMember" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi } from '../../../api/cms'
import type { Member } from '../../../api/publicPortal'
import ImageCropField from '../../../components/ImageCropField.vue'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import CmsImportStrip from './CmsImportStrip.vue'
import type { CmsListRow } from '../composables/useCmsContentData'
import { useCmsEditorMutation } from '../composables/useCmsEditorMutation'

defineProps<{
  rows: CmsListRow<Member>[]
  importing: boolean
  importProgress: number
}>()

const emit = defineEmits<{
  import: [file: File]
  changed: []
}>()

type MemberForm = Record<string, unknown> & {
  name: string
  role_type: string
  research_direction: string
  email: string
  avatar?: File
  profile: string
  sort_order: number
}
const editingId = ref<number | null>(null)
const currentAvatar = ref('')
const currentAvatarSize = ref(0)
const form = reactive<MemberForm>({ name: '', role_type: '', research_direction: '', email: '', avatar: undefined, profile: '', sort_order: 0 })
const { saving, progress, save, remove } = useCmsEditorMutation(async () => emit('changed'))

function resetMember() {
  editingId.value = null
  currentAvatar.value = ''
  currentAvatarSize.value = 0
  Object.assign(form, { name: '', role_type: '', research_direction: '', email: '', avatar: undefined, profile: '', sort_order: 0 })
}

function editMember(item: Member) {
  editingId.value = item.id
  currentAvatar.value = item.avatar || ''
  currentAvatarSize.value = item.avatar_size || 0
  Object.assign(form, {
    name: item.name,
    role_type: item.role_label || item.role_type || '',
    research_direction: item.research_direction || '',
    email: item.email || '',
    avatar: undefined,
    profile: item.profile || '',
    sort_order: item.sort_order || 0,
  })
}

async function saveMember() {
  if (!form.name.trim()) {
    ElMessage.warning('请填写成员姓名。')
    return
  }
  const id = editingId.value
  const succeeded = await save((onUploadProgress) =>
    id ? cmsApi.updateMember(id, form, onUploadProgress) : cmsApi.createMember(form, onUploadProgress),
  )
  if (succeeded) resetMember()
}

async function deleteMember() {
  const id = editingId.value
  if (!id) return
  const succeeded = await remove('确定删除这个团队成员吗？', () => cmsApi.deleteMember(id))
  if (succeeded) resetMember()
}
</script>
