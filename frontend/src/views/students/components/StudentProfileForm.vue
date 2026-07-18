<template>
  <aside class="card student-profile-editor" :aria-label="student ? '编辑学生档案' : '新建学生档案'">
    <header class="editor-heading">
      <div>
        <h2>{{ student ? '编辑学生档案' : '新建学生档案' }}</h2>
        <p>{{ canManage ? '关联学生账号并维护基本档案信息。' : '维护你的基本档案信息。' }}</p>
      </div>
      <button class="editor-close" type="button" title="关闭编辑" aria-label="关闭编辑" @click="$emit('cancel')">
        <el-icon><Close /></el-icon>
      </button>
    </header>

    <div class="editor-body">
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
    </div>

    <footer class="editor-footer">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">{{ student ? '保存修改' : '创建档案' }}</el-button>
    </footer>
  </aside>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
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


watch(
  [() => props.open, () => props.student],
  ([open]) => {
    if (open) resetForm()
  },
  { immediate: true },
)
</script>

<style scoped>
.student-profile-editor {
  position: sticky;
  top: 16px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 32px);
  min-width: 0;
  overflow: hidden;
  padding: 0;
  box-shadow: var(--shadow-flat);
}

.student-profile-editor:hover {
  border-color: var(--color-border);
  transform: none;
}

.editor-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px solid var(--color-line);
  padding: 16px 18px 14px;
}

.editor-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.editor-heading p {
  margin: 5px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
}

.editor-close {
  display: inline-grid;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-muted);
  cursor: pointer;
}

.editor-close:hover {
  border-color: rgba(0, 135, 60, 0.24);
  color: var(--color-cau-green);
}

.editor-body {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 18px 4px;
}

.editor-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  padding: 13px 18px;
  background: var(--color-panel);
}

.form-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 900px) {
  .student-profile-editor {
    position: static;
    max-height: none;
  }
}

@media (max-width: 520px) {
  .form-pair {
    grid-template-columns: 1fr;
  }

  .editor-footer .el-button {
    flex: 1;
    margin: 0;
  }
}
</style>
