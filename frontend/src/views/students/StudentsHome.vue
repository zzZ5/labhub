<template>
  <InternalLayout title="学生档案">
    <section class="student-page">
      <header class="surface-heading student-heading">
        <div>
          <h1>学生档案</h1>
          <p>学生档案用于保存导师信息、研究方向、开题、中期、论文和答辩等资料；成员管理负责登录账号和系统角色。二者通过“关联成员账号”打通。</p>
        </div>
        <el-button v-if="canManageStudents" type="primary" @click="startCreate">新建学生档案</el-button>
      </header>

      <section class="student-workspace">
        <StudentList
          v-model:keyword="studentKeyword"
          v-model:degree="degreeFilter"
          :students="pagedStudents"
          :all-count="students.length"
          :total="filteredStudents.length"
          :selected-id="selectedStudent?.id || null"
          :page="studentPage"
          :total-pages="studentTotalPages"
          @select="selectStudent"
          @update:page="studentPage = $event"
        />

        <main class="archive-panel">
          <StudentProfileSummary
            v-if="selectedStudent"
            :student="selectedStudent"
            @edit="startEdit"
            @delete="confirmDeleteProfile"
            @upload="openUpload"
          />
          <StudentArchiveList v-if="selectedStudent" :files="displayFiles" @delete="confirmDeleteArchiveFile" />
        </main>

        <StudentProfileForm
          :open="formVisible"
          :student="editingStudent"
          :current-student="selectedStudent || null"
          :student-users="studentUserOptions"
          :supervisors="supervisorOptions"
          :can-manage="canManageStudents"
          :default-user-id="session.user?.id || 0"
          :default-name="session.displayName"
          :saving="savingProfile"
          @save="saveProfile"
          @cancel="cancelEdit"
          @edit-current="selectedStudent && startEdit(selectedStudent)"
        />
      </section>

      <StudentArchiveUploadDialog
        v-model:open="uploadVisible"
        :saving="uploading"
        :progress="uploadProgress"
        @save="submitArchiveFile"
      />
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { fetchUsers, type CurrentUser } from '../../api/accounts'
import {
  createStudentProfile,
  deleteStudentArchiveFile,
  deleteStudentProfile,
  fetchStudentProfiles,
  type StudentArchiveFile,
  type StudentArchiveUploadPayload,
  type StudentProfile,
  type StudentProfilePayload,
  updateStudentProfile,
  uploadStudentArchiveFile,
} from '../../api/students'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { useSessionStore } from '../../stores/session'
import StudentArchiveList from './components/StudentArchiveList.vue'
import StudentArchiveUploadDialog from './components/StudentArchiveUploadDialog.vue'
import StudentList from './components/StudentList.vue'
import StudentProfileForm from './components/StudentProfileForm.vue'
import StudentProfileSummary from './components/StudentProfileSummary.vue'
import { useStudentDirectory } from './composables/useStudentDirectory'

const session = useSessionStore()
const route = useRoute()
const students = ref<StudentProfile[]>([])
const users = ref<CurrentUser[]>([])
const {
  selectedId,
  studentKeyword,
  degreeFilter,
  studentPage,
  filteredStudents,
  studentTotalPages,
  pagedStudents,
  selectedStudent,
  selectStudent: selectDirectoryStudent,
  reconcileSelection,
} = useStudentDirectory(students)
const uploadVisible = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const formVisible = ref(false)
const savingProfile = ref(false)
const editingStudent = ref<StudentProfile | null>(null)
const displayFiles = computed<StudentArchiveFile[]>(() => selectedStudent.value?.archive_files || [])
const canManageStudents = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin'])))
const usedUserIds = computed(() => new Set(students.value.filter((item) => item.id !== editingStudent.value?.id).map((item) => item.user)))
const studentUserOptions = computed(() => {
  const candidates = canManageStudents.value
    ? users.value.filter(isStudentAccount)
    : users.value.filter((user) => user.id === session.user?.id && isStudentAccount(user))
  return candidates.filter((user) => !usedUserIds.value.has(user.id) || user.id === editingStudent.value?.user)
})
const supervisorOptions = computed(() =>
  users.value.filter((user) => user.is_superuser || user.roles.includes('admin') || user.profile?.school_identity === 'pi'),
)

function isStudentAccount(user: CurrentUser) {
  const identity = user.profile?.school_identity
  return user.roles.includes('undergraduate') || user.roles.includes('master') || user.roles.includes('phd') || identity === 'undergraduate' || identity === 'master' || identity === 'phd'
}

function selectStudent(id: number) {
  selectDirectoryStudent(id)
  formVisible.value = false
}

function startCreate() {
  editingStudent.value = null
  formVisible.value = true
}

function startEdit(student: StudentProfile) {
  editingStudent.value = student
  formVisible.value = true
}

function cancelEdit() {
  formVisible.value = false
  editingStudent.value = null
}

async function saveProfile(payload: StudentProfilePayload) {
  savingProfile.value = true
  try {
    const saved = editingStudent.value
      ? await updateStudentProfile(editingStudent.value.id, payload)
      : await createStudentProfile(payload)
    ElMessage.success('学生档案已保存。')
    formVisible.value = false
    editingStudent.value = null
    await loadStudents(saved.id)
  } catch (error: any) {
    const detail = error?.response?.data?.detail || Object.values(error?.response?.data || {})?.[0]
    ElMessage.error(String(detail || '保存失败，请检查账号是否已绑定其他学生档案。'))
  } finally {
    savingProfile.value = false
  }
}

function openUpload() {
  uploadProgress.value = 0
  uploadVisible.value = true
}

function uploadErrorMessage(error: any) {
  const data = error?.response?.data
  if (data?.detail) return data.detail
  if (data?.file?.length) return data.file[0]
  if (error?.code === 'ECONNABORTED') return '上传超时，请检查网络或稍后重试。'
  if (!error?.response) return '上传连接失败，请检查网络或服务器上传大小限制。'
  return '上传失败，请确认权限和表单内容。'
}

async function submitArchiveFile(payload: StudentArchiveUploadPayload) {
  if (!selectedStudent.value) return
  uploading.value = true
  uploadProgress.value = 0
  try {
    await uploadStudentArchiveFile({
      student: selectedStudent.value.id,
      ...payload,
    }, (event) => {
      if (!event.total) return
      uploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    uploadProgress.value = 100
    ElMessage.success('学生资料已上传。')
    uploadVisible.value = false
    await loadStudents(selectedStudent.value.id)
  } catch (error: any) {
    ElMessage.error(uploadErrorMessage(error))
  } finally {
    uploading.value = false
    setTimeout(() => {
      if (!uploading.value) uploadProgress.value = 0
    }, 800)
  }
}

async function confirmDeleteProfile(student: StudentProfile) {
  try {
    await ElMessageBox.confirm(
      `确定删除“${student.name}”的学生档案吗？该档案下的归档资料也会一起删除。`,
      '删除学生档案',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }
  try {
    await deleteStudentProfile(student.id)
    ElMessage.success('学生档案已删除。')
    formVisible.value = false
    await loadStudents()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '删除失败，请确认权限。')
  }
}

async function confirmDeleteArchiveFile(file: StudentArchiveFile) {
  try {
    await ElMessageBox.confirm(`确定删除资料“${file.title}”吗？`, '删除归档资料', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    await deleteStudentArchiveFile(file.id)
    ElMessage.success('归档资料已删除。')
    await loadStudents(selectedStudent.value?.id)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '删除失败，请确认权限。')
  }
}

async function loadStudents(preferredId?: number) {
  students.value = await fetchStudentProfiles()
  const ownStudent = route.query.mine === '1' ? students.value.find((student) => student.user === session.user?.id) : undefined
  reconcileSelection(preferredId || ownStudent?.id)
}

async function loadUsers() {
  if (!session.initialized) await session.loadCurrentUser()
  try {
    users.value = canManageStudents.value ? await fetchUsers() : session.user ? [session.user] : []
  } catch {
    users.value = session.user ? [session.user] : []
  }
}

onMounted(async () => {
  await loadUsers()
  await loadStudents()
})

watch(() => route.query.mine, (mine) => {
  if (mine !== '1') return
  const ownStudent = students.value.find((student) => student.user === session.user?.id)
  if (ownStudent) selectStudent(ownStudent.id)
})
</script>

<style scoped>
.student-page,
.archive-panel {
  display: grid;
  gap: 14px;
}

.student-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
}

.student-workspace {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr) 330px;
  gap: 18px;
}

@media (max-width: 1280px) {
  .student-workspace {
    grid-template-columns: 260px minmax(0, 1fr);
  }

  .edit-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 900px) {
  .student-heading,
  .student-workspace {
    grid-template-columns: 1fr;
  }

  .student-heading {
    display: grid;
  }
}
</style>


