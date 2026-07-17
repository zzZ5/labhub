<template>
  <el-drawer
    :model-value="open"
    class="entity-form-drawer"
    :title="student ? '编辑学生档案' : '新建学生档案'"
    size="min(520px, 100%)"
    destroy-on-close
    @update:model-value="handleOpenChange"
  >
    <p class="entity-form-intro">{{ canManage ? '关联学生账号并维护基本档案信息。' : '维护你的基本档案信息。' }}</p>
    <el-form label-position="top" class="entity-form profile-form">
      <el-form-item label="头像">
        <ImageCropField v-model="form.avatar_upload" :existing-url="avatarPreview" :existing-size="student?.avatar_size || currentStudent?.avatar_size || 0" :aspect-ratio="1" :output-width="800" :output-height="800" :max-size-mb="10" preview-shape="circle" @preview="avatarPreview = $event" />
      </el-form-item>
      <el-form-item label="关联成员账号">
        <el-select v-model="form.user" filterable placeholder="选择学生登录账号" :disabled="!canManage && Boolean(student)">
          <el-option v-for="user in studentUsers" :key="user.id" :label="userOptionLabel(user)" :value="user.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
      <div class="form-pair">
        <el-form-item label="学位类型">
          <el-select v-model="form.degree_type">
            <el-option label="本科" value="undergraduate" />
            <el-option label="硕士" value="master" />
            <el-option label="博士" value="phd" />
          </el-select>
        </el-form-item>
        <el-form-item label="年级"><el-input v-model="form.grade" placeholder="如 2024级" /></el-form-item>
      </div>
      <el-form-item label="导师">
        <el-select v-model="form.advisors" multiple collapse-tags collapse-tags-tooltip clearable filterable placeholder="可选择多位导师">
          <el-option v-for="user in supervisors" :key="user.id" :label="userOptionLabel(user)" :value="user.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="研究方向"><el-input v-model="form.research_direction" /></el-form-item>
      <el-form-item label="研究题目"><el-input v-model="form.research_topic" type="textarea" :rows="3" /></el-form-item>
    </el-form>
    <template #footer>
      <div class="entity-form-footer">
        <el-button @click="$emit('cancel')">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ student ? '保存修改' : '创建档案' }}</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { CurrentUser } from '../../../api/accounts'
import type { StudentProfile, StudentProfilePayload } from '../../../api/students'
import ImageCropField from '../../../components/ImageCropField.vue'

const props = defineProps<{
  open: boolean
  student: StudentProfile | null
  currentStudent: StudentProfile | null
  studentUsers: CurrentUser[]
  supervisors: CurrentUser[]
  canManage: boolean
  defaultUserId: number
  defaultName: string
  saving: boolean
}>()

const emit = defineEmits<{
  save: [payload: StudentProfilePayload]
  cancel: []
  editCurrent: []
}>()

const avatarPreview = ref('')
const form = reactive<StudentProfilePayload>({ user: 0, name: '', degree_type: 'master', grade: '', supervisor: null, advisors: [], research_topic: '', research_direction: '' })

function resetForm() {
  const student = props.student
  Object.assign(form, {
    user: student?.user || props.defaultUserId,
    name: student?.name || props.defaultName,
    degree_type: student?.degree_type || 'master',
    grade: student?.grade || '',
    advisors: student?.advisors?.length ? [...student.advisors] : student?.supervisor ? [student.supervisor] : [],
    supervisor: student?.supervisor || null,
    research_topic: student?.research_topic || '',
    research_direction: student?.research_direction || '',
    enrollment_date: student?.enrollment_date || null,
    graduation_date: student?.graduation_date || null,
    destination: student?.destination || '',
    avatar_upload: undefined,
  })
  avatarPreview.value = student?.avatar || ''
}

function userOptionLabel(user: CurrentUser) {
  const name = user.profile?.real_name || user.first_name || user.username
  return `${name}（${user.email || user.username}）`
}

function submit() {
  if (!form.user || !form.name.trim()) {
    ElMessage.warning('请填写姓名并关联成员账号。')
    return
  }
  const advisors = [...(form.advisors || [])]
  emit('save', { ...form, name: form.name.trim(), advisors, supervisor: advisors[0] || null })
}

function handleOpenChange(value: boolean) {
  if (!value) emit('cancel')
}

watch(
  [() => props.open, () => props.student],
  ([open]) => {
    if (open) resetForm()
  },
  { immediate: true },
)
</script>

<style scoped>
.student-avatar-editor {
  display: flex;
  align-items: center;
  gap: 12px;
}

.student-profile-avatar {
  display: grid;
  width: 52px;
  height: 52px;
  place-items: center;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: 50%;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 700;
}

.student-profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.student-avatar-upload {
  border: 1px solid rgba(0, 135, 60, 0.24);
  border-radius: var(--radius-sm);
  padding: 7px 12px;
  color: var(--color-cau-green);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.student-avatar-upload input {
  display: none;
}

.avatar-note {
  color: var(--color-muted);
  font-size: 12px;
}

.form-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.relation-note {
  display: grid;
  gap: 10px;
}

@media (max-width: 520px) {
  .form-pair {
    grid-template-columns: 1fr;
  }
}
</style>
