<template>
  <InternalLayout title="学生档案">
    <section class="student-page">
      <InternalPageHeader class="student-heading">
        <p>集中查看学生信息、导师关系和开题、中期、论文、答辩等归档资料。</p>
        <template #actions><el-button v-if="canManageStudents" type="primary" @click="startCreate">新建学生档案</el-button></template>
      </InternalPageHeader>

      <LoadErrorNotice v-if="loadError" :description="loadError" :retrying="loading" @retry="reloadStudentsPage" />

      <section :class="['student-workspace', { 'show-mobile-detail': mobileDetailOpen, 'is-editing': formVisible }]">
        <StudentList
          class="student-directory"
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
          <button class="mobile-directory-back" type="button" @click="closeMobileDetail">返回学生列表</button>
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
          v-if="formVisible"
          class="student-editor"
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
import InternalPageHeader from '../../components/InternalPageHeader.vue'
import LoadErrorNotice from '../../components/LoadErrorNotice.vue'
import { useSessionStore } from '../../stores/session'
import StudentArchiveList from './components/StudentArchiveList.vue'
import StudentArchiveUploadDialog from './components/StudentArchiveUploadDialog.vue'
import StudentList from './components/StudentList.vue'
import StudentProfileForm from './components/StudentProfileForm.vue'
import StudentProfileSummary from './components/StudentProfileSummary.vue'
import { useStudentDirectory } from './composables/useStudentDirectory'
import { requestErrorMessage } from '../../utils/requestErrors'

const session = useSessionStore()
const route = useRoute()
const students = ref<StudentProfile[]>([])
const users = ref<CurrentUser[]>([])
const loading = ref(false)
const loadError = ref('')
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
const mobileDetailOpen = ref(route.query.mine === '1')
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
  mobileDetailOpen.value = true
}

function startCreate() {
  editingStudent.value = null
  formVisible.value = true
  mobileDetailOpen.value = true
}

function startEdit(student: StudentProfile) {
  editingStudent.value = student
  formVisible.value = true
  mobileDetailOpen.value = true
}

function closeMobileDetail() {
  formVisible.value = false
  mobileDetailOpen.value = false
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
    ElMessage.error(requestErrorMessage(error, '上传失败，请确认权限和表单内容。'))
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
  const queryStudentId = Math.max(0, Number(route.query.student) || 0)
  reconcileSelection(preferredId || ownStudent?.id || queryStudentId)
}

async function loadUsers() {
  if (!session.initialized) await session.loadCurrentUser()
  try {
    users.value = canManageStudents.value ? await fetchUsers() : session.user ? [session.user] : []
  } catch (error) {
    users.value = session.user ? [session.user] : []
    loadError.value = requestErrorMessage(error, '成员账号列表加载失败，学生档案仍可继续查看。')
  }
}

async function reloadStudentsPage() {
  loading.value = true
  loadError.value = ''
  try {
    await loadUsers()
    await loadStudents(selectedStudent.value?.id)
  } catch (error) {
    loadError.value = requestErrorMessage(error, '学生档案加载失败，现有内容已保留。')
  } finally {
    loading.value = false
  }
}

onMounted(reloadStudentsPage)

watch(() => route.query.mine, (mine) => {
  if (mine !== '1') return
  const ownStudent = students.value.find((student) => student.user === session.user?.id)
  if (ownStudent) selectStudent(ownStudent.id)
})

watch(() => route.query.student, (value) => {
  const id = Math.max(0, Number(value) || 0)
  if (id && students.value.some((student) => student.id === id)) selectStudent(id)
})

watch(filteredStudents, (matches) => {
  if (!studentKeyword.value.trim() || matches.length !== 1) return
  selectDirectoryStudent(matches[0].id)
  formVisible.value = false
  mobileDetailOpen.value = true
})
</script>

<style scoped>
.student-page,
.archive-panel {
  display: grid;
  gap: 14px;
}

.student-heading {
  align-items: center;
}

.mobile-directory-back {
  display: none;
}

.student-workspace {
  display: grid;
  grid-template-columns: 286px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.student-workspace.is-editing {
  grid-template-columns: 270px minmax(0, 1fr) 340px;
}

@media (max-width: 1400px) {
  .student-workspace {
    grid-template-columns: 260px minmax(0, 1fr);
  }

  .student-editor {
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

  .student-workspace:not(.show-mobile-detail) .archive-panel,
  .student-workspace:not(.show-mobile-detail) .student-editor,
  .student-workspace.show-mobile-detail .student-directory {
    display: none !important;
  }

  .student-workspace.is-editing .archive-panel { display: none; }
  .student-workspace.is-editing .student-editor { display: block; grid-column: auto; }

  .mobile-directory-back {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    min-height: 38px;
    border: 1px solid rgba(0, 135, 60, 0.22);
    border-radius: var(--radius-sm);
    padding: 0 12px;
    background: #fff;
    color: var(--color-cau-green);
    font-weight: 650;
  }

  .mobile-directory-back::before {
    margin-right: 6px;
    content: "←";
  }
}
</style>


