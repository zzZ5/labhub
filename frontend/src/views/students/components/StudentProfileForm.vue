<template>
  <aside class="card edit-panel">
    <div class="panel-heading">
      <div>
        <h2>{{ student ? '编辑学生档案' : '学生档案设置' }}</h2>
        <p>{{ canManage ? '管理员可绑定学生账号，导师信息在档案内维护。' : '你可以维护自己的学生档案。' }}</p>
      </div>
    </div>

    <el-form v-if="open" label-position="top" class="profile-form">
      <el-form-item label="头像">
        <div class="student-avatar-editor">
          <div class="student-profile-avatar">
            <img v-if="avatarPreview" :src="avatarPreview" alt="头像预览" />
            <span v-else>{{ form.name.slice(0, 1) || '学' }}</span>
          </div>
          <label class="student-avatar-upload">选择图片<input :key="fileInputKey" type="file" accept="image/*" @change="selectAvatar" /></label>
        </div>
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
      <div class="form-actions">
        <el-button @click="$emit('cancel')">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">保存档案</el-button>
      </div>
    </el-form>

    <div v-else class="relation-note">
      <strong>账号与档案</strong>
      <p>成员账号用于登录，学生档案保存学生信息和个人资料。</p>
      <el-button v-if="currentStudent?.can_edit" plain @click="$emit('editCurrent')">编辑当前档案</el-button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { CurrentUser } from '../../../api/accounts'
import type { StudentProfile, StudentProfilePayload } from '../../../api/students'

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
const fileInputKey = ref(0)
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
  fileInputKey.value += 1
}

function userOptionLabel(user: CurrentUser) {
  const name = user.profile?.real_name || user.first_name || user.username
  return `${name}（${user.email || user.username}）`
}

function selectAvatar(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  form.avatar_upload = file
  avatarPreview.value = URL.createObjectURL(file)
}

function submit() {
  if (!form.user || !form.name.trim()) {
    ElMessage.warning('请填写姓名并关联成员账号。')
    return
  }
  const advisors = [...(form.advisors || [])]
  emit('save', { ...form, name: form.name.trim(), advisors, supervisor: advisors[0] || null })
}

watch(() => props.open, (open) => {
  if (open) resetForm()
})
</script>

<style scoped>
.edit-panel {
  position: sticky;
  top: 96px;
  max-height: calc(100vh - 120px);
  overflow: auto;
  padding: 16px;
}

.edit-panel:hover {
  transform: none;
}

.panel-heading {
  margin-bottom: 14px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.panel-heading p,
.relation-note p {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

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

.form-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.relation-note {
  display: grid;
  gap: 10px;
}

@media (max-width: 1180px) {
  .edit-panel {
    position: static;
    max-height: none;
  }
}

@media (max-width: 520px) {
  .form-pair {
    grid-template-columns: 1fr;
  }
}
</style>
