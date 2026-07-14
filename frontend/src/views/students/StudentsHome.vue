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
        <aside class="card student-list">
          <div class="side-heading">
            <h2>学生列表</h2>
            <span>{{ filteredStudents.length }} / {{ students.length }} 人</span>
          </div>
          <div class="student-list-tools">
            <el-input v-model="studentKeyword" size="small" clearable placeholder="搜索姓名、年级、方向" />
            <el-select v-model="degreeFilter" size="small" placeholder="学位" clearable>
              <el-option label="本科" value="undergraduate" />
              <el-option label="硕士" value="master" />
              <el-option label="博士" value="phd" />
            </el-select>
          </div>
          <button
            v-for="student in pagedStudents"
            :key="student.id"
            :class="{ active: selectedStudent?.id === student.id }"
            @click="selectStudent(student.id)"
          >
            <strong>{{ student.name }}</strong>
            <span>{{ student.degree_label }} · {{ student.grade || '未填写年级' }}</span>
            <small>{{ student.user_email || student.user_username || '未绑定账号' }}</small>
          </button>
          <div v-if="!filteredStudents.length" class="empty-note">{{ students.length ? '没有找到匹配学生。' : '暂无学生档案。' }}</div>
          <div v-if="studentTotalPages > 1" class="student-pager">
            <button type="button" :disabled="studentPage === 1" @click="studentPage -= 1">上一页</button>
            <span>{{ studentPage }} / {{ studentTotalPages }}</span>
            <button type="button" :disabled="studentPage === studentTotalPages" @click="studentPage += 1">下一页</button>
          </div>
        </aside>

        <main class="archive-panel">
          <section v-if="selectedStudent" class="card profile-card">
            <div class="profile-heading">
              <div>
                <h1>{{ selectedStudent.name }}</h1>
                <p>{{ selectedStudent.research_direction || selectedStudent.research_topic || '研究方向待补充' }}</p>
              </div>
              <div class="profile-actions">
                <el-button v-if="selectedStudent.can_edit" plain @click="startEdit(selectedStudent)">编辑档案</el-button>
                <el-button v-if="selectedStudent.can_delete" plain type="danger" @click="confirmDeleteProfile(selectedStudent)">删除档案</el-button>
                <el-button v-if="selectedStudent.can_edit" type="primary" @click="openUpload">上传资料</el-button>
              </div>
            </div>

            <dl class="profile-list">
              <div>
                <dt>身份</dt>
                <dd>{{ selectedStudent.degree_label }} {{ selectedStudent.grade || '' }}</dd>
              </div>
              <div>
                <dt>导师</dt>
                <dd>{{ advisorText(selectedStudent) }}</dd>
              </div>
              <div>
                <dt>研究题目</dt>
                <dd>{{ selectedStudent.research_topic || '-' }}</dd>
              </div>
              <div>
                <dt>可见范围</dt>
                <dd>{{ selectedStudent.visibility_label }}</dd>
              </div>
              <div>
                <dt>登录账号</dt>
                <dd>{{ selectedStudent.user_email || selectedStudent.user_username || '-' }}</dd>
              </div>
              <div>
                <dt>账号权限</dt>
                <dd>在成员管理中维护</dd>
              </div>
            </dl>
          </section>
<section v-if="selectedStudent" class="card files-panel">
            <div class="panel-heading">
              <div>
                <h2>归档资料</h2>
                <p>用于保存开题、中期、毕业论文、答辩材料和其它个人归档资料。</p>
              </div>
              <span class="status-tag normal">{{ displayFiles.length }} 份资料</span>
            </div>

            <div v-if="displayFiles.length" class="file-grid">
              <article v-for="file in displayFiles" :key="file.id" class="file-card">
                <div class="file-icon" :class="archiveKind(file)">
                  <el-icon><component :is="archiveIcon(file)" /></el-icon>
                </div>
                <div class="file-main">
                  <div class="file-title-row">
                    <strong>{{ file.title }}</strong>
                    <span>{{ archiveTypeLabel(file) }}</span>
                  </div>
                  <div class="file-meta">
                    <span>{{ file.file_type_label }}</span>
                    <span>{{ archiveFileSizeLabel(file) }}</span>
                    <span v-if="file.visibility_label">{{ file.visibility_label }}</span>
                  </div>
                  <p>{{ file.description || file.original_filename || '未记录原始文件名' }}</p>
                </div>
                <div class="file-actions">
                  <a
                    v-if="file.can_view && canPreviewArchive(file)"
                    class="file-primary-action"
                    :href="previewStudentArchiveFileUrl(file)"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <el-icon><View /></el-icon>
                    {{ archivePreviewLabel(file) }}
                  </a>
                  <span v-else-if="file.can_view" class="file-preview-note">{{ archivePreviewStatus(file) }}</span>
                  <a v-if="file.can_view" class="file-secondary-action" :href="downloadStudentArchiveFileUrl(file)">
                    <el-icon><Download /></el-icon>
                    下载原文件
                  </a>
                  <el-button v-if="file.can_delete" size="small" plain type="danger" @click="confirmDeleteArchiveFile(file)">删除</el-button>
                  <el-button v-else-if="!file.can_view" disabled>无权限</el-button>
                </div>
              </article>
            </div>
            <div v-else class="empty-note">暂无归档资料。</div>
          </section>
        </main>

        <aside class="card edit-panel">
          <div class="panel-heading compact">
            <div>
              <h2>{{ editingId ? '编辑学生档案' : '学生档案设置' }}</h2>
              <p>{{ canManageStudents ? '管理员可绑定学生账号，导师信息在档案内维护。' : '你可以维护自己的学生档案。' }}</p>
            </div>
          </div>

          <el-form v-if="formVisible" label-position="top" class="profile-form">
            <el-form-item label="关联成员账号">
              <el-select v-model="profileForm.user" filterable placeholder="选择学生登录账号" :disabled="!canManageStudents && Boolean(editingId)">
                <el-option
                  v-for="user in studentUserOptions"
                  :key="user.id"
                  :label="userOptionLabel(user)"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="profileForm.name" />
            </el-form-item>
            <div class="form-pair">
              <el-form-item label="学位类型">
                <el-select v-model="profileForm.degree_type">
                  <el-option label="本科" value="undergraduate" />
                  <el-option label="硕士" value="master" />
                  <el-option label="博士" value="phd" />
                </el-select>
              </el-form-item>
              <el-form-item label="年级">
                <el-input v-model="profileForm.grade" placeholder="如 2024级" />
              </el-form-item>
            </div>
            <el-form-item label="导师">
              <el-select v-model="profileForm.advisors" multiple collapse-tags collapse-tags-tooltip clearable filterable placeholder="可选择多位导师">
                <el-option
                  v-for="user in supervisorOptions"
                  :key="user.id"
                  :label="userOptionLabel(user)"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="研究方向">
              <el-input v-model="profileForm.research_direction" />
            </el-form-item>
            <el-form-item label="研究题目">
              <el-input v-model="profileForm.research_topic" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="可见范围">
              <el-select v-model="profileForm.visibility">
                <el-option label="本人可见" value="private" />
                <el-option label="本人/导师可见" value="supervisor" />
                <el-option label="硕博导师/管理员可见" value="pi" />
                <el-option label="成员可见" value="members" />
              </el-select>
            </el-form-item>
            <div class="form-actions">
              <el-button @click="cancelEdit">取消</el-button>
              <el-button type="primary" :loading="savingProfile" @click="saveProfile">保存档案</el-button>
            </div>
          </el-form>

          <div v-else class="relation-note">
            <strong>当前逻辑</strong>
            <p>成员账号决定能不能登录；学生档案决定这个账号对应哪位学生、能上传哪些个人资料。</p>
            <el-button v-if="selectedStudent?.can_edit" plain @click="startEdit(selectedStudent)">编辑当前档案</el-button>
          </div>
        </aside>
      </section>

      <el-dialog v-model="uploadVisible" title="上传学生资料" width="560px">
        <el-form label-position="top">
          <el-form-item label="资料类型">
            <el-select v-model="uploadForm.file_type">
              <el-option label="开题报告" value="proposal_report" />
              <el-option label="开题 PPT" value="proposal_ppt" />
              <el-option label="中期报告" value="midterm_report" />
              <el-option label="中期 PPT" value="midterm_ppt" />
              <el-option label="毕业论文" value="thesis" />
              <el-option label="答辩 PPT" value="defense_ppt" />
              <el-option label="发表论文" value="paper" />
              <el-option label="其它" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="标题">
            <el-input v-model="uploadForm.title" placeholder="例如：硕士毕业论文终稿" />
          </el-form-item>
          <el-form-item label="说明">
            <el-input v-model="uploadForm.description" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="可见范围">
            <el-select v-model="uploadForm.visibility">
              <el-option label="组内成员可见" value="members" />
              <el-option label="仅本人可见" value="private" />
              <el-option label="本人和导师可见" value="supervisor" />
              <el-option label="硕博导师和管理员可见" value="pi" />
            </el-select>
          </el-form-item>
          <el-form-item label="文件">
            <input class="file-input" type="file" accept=".pdf,.doc,.docx,.ppt,.pptx" @change="handleFileChange" />
            <small v-if="uploadForm.file" class="upload-file-note">{{ uploadForm.file.name }}（{{ formatFileSize(uploadForm.file.size) }}）</small>
          </el-form-item>
        </el-form>
      <template #footer>
        <div v-if="uploading || uploadProgress > 0" class="upload-progress dialog-upload-progress">
          <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
          <span>{{ uploadProgress < 100 ? '正在上传，请不要关闭窗口。' : '上传完成，正在保存记录。' }}</span>
        </div>
        <el-button @click="uploadVisible = false">取消</el-button>
          <el-button type="primary" :loading="uploading" @click="submitArchiveFile">保存资料</el-button>
        </template>
      </el-dialog>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Download, Document, Files, PictureFilled, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { fetchUsers, type CurrentUser } from '../../api/accounts'
import {
  createStudentProfile,
  deleteStudentArchiveFile,
  deleteStudentProfile,
  downloadStudentArchiveFileUrl,
  fetchStudentProfiles,
  previewStudentArchiveFileUrl,
  type StudentArchiveFile,
  type StudentProfile,
  type StudentProfilePayload,
  updateStudentProfile,
  uploadStudentArchiveFile,
} from '../../api/students'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { useSessionStore } from '../../stores/session'

const session = useSessionStore()
const students = ref<StudentProfile[]>([])
const users = ref<CurrentUser[]>([])
const selectedId = ref<number | null>(null)
const uploadVisible = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const formVisible = ref(false)
const savingProfile = ref(false)
const editingId = ref<number | null>(null)
const studentKeyword = ref('')
const degreeFilter = ref('')
const studentPage = ref(1)
const studentPageSize = 12

const profileForm = reactive<StudentProfilePayload>({
  user: 0,
  name: '',
  degree_type: 'master',
  grade: '',
  supervisor: null,
  advisors: [],
  research_topic: '',
  research_direction: '',
  enrollment_date: null,
  graduation_date: null,
  destination: '',
  visibility: 'supervisor',
})

const uploadForm = reactive({
  file_type: 'proposal_report',
  title: '',
  visibility: 'members',
  description: '',
  file: undefined as File | undefined,
})

const filteredStudents = computed(() => {
  const keyword = studentKeyword.value.trim().toLowerCase()
  return students.value.filter((student) => {
    const matchesDegree = !degreeFilter.value || student.degree_type === degreeFilter.value
    const haystack = `${student.name} ${student.grade} ${student.research_direction} ${student.research_topic} ${student.user_email} ${student.user_username}`.toLowerCase()
    return matchesDegree && (!keyword || haystack.includes(keyword))
  })
})
const studentTotalPages = computed(() => Math.max(1, Math.ceil(filteredStudents.value.length / studentPageSize)))
const pagedStudents = computed(() => filteredStudents.value.slice((studentPage.value - 1) * studentPageSize, studentPage.value * studentPageSize))
const selectedStudent = computed(() => students.value.find((item) => item.id === selectedId.value) || filteredStudents.value[0] || students.value[0])
const displayFiles = computed<StudentArchiveFile[]>(() => selectedStudent.value?.archive_files || [])
const canManageStudents = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin', 'pi'])))
const usedUserIds = computed(() => new Set(students.value.filter((item) => item.id !== editingId.value).map((item) => item.user)))
const studentUserOptions = computed(() => {
  const candidates = canManageStudents.value
    ? users.value.filter(isStudentAccount)
    : users.value.filter((user) => user.id === session.user?.id && isStudentAccount(user))
  return candidates.filter((user) => !usedUserIds.value.has(user.id) || user.id === profileForm.user)
})
const supervisorOptions = computed(() =>
  users.value.filter((user) => user.is_superuser || user.roles.includes('admin') || user.roles.includes('pi')),
)

function isStudentAccount(user: CurrentUser) {
  const identity = user.profile?.role_type
  return user.roles.includes('undergraduate') || user.roles.includes('master') || user.roles.includes('phd') || identity === 'undergraduate' || identity === 'master' || identity === 'phd'
}

function advisorText(student: StudentProfile) {
  if (student.advisor_names?.length) return student.advisor_names.join('、')
  return student.supervisor_name || '-'
}

function userOptionLabel(user: CurrentUser) {
  const name = user.profile?.real_name || user.first_name || user.username
  return `${name}（${user.email || user.username}）`
}

function archiveFilename(file: StudentArchiveFile) {
  return (file.original_filename || file.file || file.title).toLowerCase()
}

function archiveKind(file: StudentArchiveFile) {
  const filename = archiveFilename(file)
  if (filename.endsWith('.pdf')) return 'pdf'
  if (filename.endsWith('.doc') || filename.endsWith('.docx')) return 'word'
  if (filename.endsWith('.ppt') || filename.endsWith('.pptx')) return 'ppt'
  if (filename.endsWith('.png') || filename.endsWith('.jpg') || filename.endsWith('.jpeg')) return 'image'
  return 'file'
}

function archiveTypeLabel(file: StudentArchiveFile) {
  const labels: Record<string, string> = {
    pdf: 'PDF',
    word: 'Word',
    ppt: 'PPT',
    image: '图片',
    file: '文件',
  }
  return labels[archiveKind(file)]
}

function archiveFileSizeLabel(file: StudentArchiveFile) {
  return file.file_size ? formatFileSize(file.file_size) : '大小未知'
}

function archivePreviewLabel(file: StudentArchiveFile) {
  const kind = archiveKind(file)
  if (kind === 'pdf' || kind === 'word' || kind === 'ppt') return '在线查看'
  if (kind === 'image') return '查看图片'
  return '查看文件'
}

function canPreviewArchive(file: StudentArchiveFile) {
  const kind = archiveKind(file)
  if (kind === 'word' || kind === 'ppt') return file.preview_status === 'ready'
  return true
}

function archivePreviewStatus(file: StudentArchiveFile) {
  if (file.preview_status === 'pending') return '正在生成预览'
  if (file.preview_status === 'failed') return '预览生成失败'
  if (archiveKind(file) === 'ppt' || archiveKind(file) === 'word') return '暂无在线预览'
  return '不可查看'
}

function archiveIcon(file: StudentArchiveFile) {
  const kind = archiveKind(file)
  if (kind === 'ppt') return Files
  if (kind === 'image') return PictureFilled
  return Document
}

function selectStudent(id: number) {
  selectedId.value = id
  formVisible.value = false
}

function fillProfileForm(student?: StudentProfile) {
  editingId.value = student?.id ?? null
  profileForm.user = student?.user || session.user?.id || 0
  profileForm.name = student?.name || session.displayName || ''
  profileForm.degree_type = student?.degree_type || 'master'
  profileForm.grade = student?.grade || ''
  profileForm.advisors = student?.advisors?.length ? [...student.advisors] : student?.supervisor ? [student.supervisor] : []
  profileForm.supervisor = profileForm.advisors[0] || null
  profileForm.research_topic = student?.research_topic || ''
  profileForm.research_direction = student?.research_direction || ''
  profileForm.enrollment_date = student?.enrollment_date || null
  profileForm.graduation_date = student?.graduation_date || null
  profileForm.destination = student?.destination || ''
  profileForm.visibility = student?.visibility || 'supervisor'
}

function startCreate() {
  fillProfileForm()
  formVisible.value = true
}

function startEdit(student: StudentProfile) {
  fillProfileForm(student)
  formVisible.value = true
}

function cancelEdit() {
  formVisible.value = false
  editingId.value = null
}

async function saveProfile() {
  if (!profileForm.user) {
    ElMessage.warning('请选择要绑定的成员账号。')
    return
  }
  if (!profileForm.name.trim()) {
    ElMessage.warning('请填写学生姓名。')
    return
  }
  savingProfile.value = true
  const payload = { ...profileForm, name: profileForm.name.trim(), supervisor: profileForm.advisors?.[0] || null }
  try {
    const saved = editingId.value
      ? await updateStudentProfile(editingId.value, payload)
      : await createStudentProfile(payload)
    ElMessage.success('学生档案已保存。')
    formVisible.value = false
    await loadStudents(saved.id)
  } catch (error: any) {
    const detail = error?.response?.data?.detail || Object.values(error?.response?.data || {})?.[0]
    ElMessage.error(String(detail || '保存失败，请检查账号是否已绑定其他学生档案。'))
  } finally {
    savingProfile.value = false
  }
}

function openUpload() {
  uploadForm.file = undefined
  uploadVisible.value = true
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  uploadForm.file = input.files?.[0]
  uploadProgress.value = 0
}

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function uploadErrorMessage(error: any) {
  const data = error?.response?.data
  if (data?.detail) return data.detail
  if (data?.file?.length) return data.file[0]
  if (error?.code === 'ECONNABORTED') return '上传超时，请检查网络或稍后重试。'
  if (!error?.response) return '上传连接失败，请检查网络或服务器上传大小限制。'
  return '上传失败，请确认权限和表单内容。'
}

async function submitArchiveFile() {
  if (!selectedStudent.value || !uploadForm.file) {
    ElMessage.warning('请先选择文件。')
    return
  }
  if (!uploadForm.title.trim()) {
    ElMessage.warning('请填写资料标题。')
    return
  }
  uploading.value = true
  uploadProgress.value = 0
  try {
    await uploadStudentArchiveFile({
      student: selectedStudent.value.id,
      file_type: uploadForm.file_type,
      title: uploadForm.title.trim(),
      file: uploadForm.file,
      visibility: uploadForm.visibility,
      description: uploadForm.description,
    }, (event) => {
      if (!event.total) return
      uploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    uploadProgress.value = 100
    ElMessage.success('学生资料已上传。')
    uploadVisible.value = false
    uploadForm.title = ''
    uploadForm.visibility = 'members'
    uploadForm.description = ''
    uploadForm.file = undefined
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
  selectedId.value = preferredId || selectedStudent.value?.id || filteredStudents.value[0]?.id || students.value[0]?.id || null
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

watch([studentKeyword, degreeFilter], () => {
  studentPage.value = 1
  if (filteredStudents.value.length && !filteredStudents.value.some((student) => student.id === selectedId.value)) {
    selectedId.value = filteredStudents.value[0].id
  }
})

watch(studentTotalPages, (total) => {
  if (studentPage.value > total) studentPage.value = total
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

.student-list,
.profile-card,
.files-panel,
.edit-panel {
  padding: 16px;
}

.student-list,
.edit-panel {
  position: sticky;
  top: 96px;
  max-height: calc(100vh - 120px);
  overflow: auto;
}

.student-list:hover,
.profile-card:hover,
.files-panel:hover,
.edit-panel:hover {
  transform: none;
}

.side-heading,
.panel-heading,
.profile-heading,
.profile-actions {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.panel-heading,
.side-heading {
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
}

.panel-heading.compact {
  margin-bottom: 14px;
}

.side-heading h2,
.panel-heading h2,
.profile-heading h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-weight: 650;
}

.side-heading h2,
.panel-heading h2 {
  font-size: 19px;
}

.side-heading span,
.panel-heading p,
.profile-heading p,
.student-list small,
.account-grid span,
.account-grid small,
.relation-note p {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

.profile-heading h1 {
  margin-top: 0;
  font-size: clamp(22px, 2.4vw, 28px);
  line-height: 1.2;
}

.profile-actions {
  flex: 0 0 auto;
}

.student-list-tools {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 92px;
  gap: 10px;
  margin-bottom: 14px;
}

.student-list-tools :deep(.el-input__wrapper),
.student-list-tools :deep(.el-select__wrapper) {
  min-height: 38px;
  border-radius: var(--radius-sm);
  box-shadow: 0 0 0 1px var(--color-border) inset;
}

.student-list-tools :deep(.el-input__wrapper:hover),
.student-list-tools :deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(0, 135, 60, 0.24) inset;
}

.student-list button {
  display: grid;
  gap: 3px;
  width: 100%;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  padding: 9px 11px;
  background: #fff;
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
}

.student-list button.active,
.student-list button:hover {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
}

.student-list button.active {
  color: var(--color-cau-green);
}

.student-list strong,
.student-list span,
.student-list small {
  display: block;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-list strong {
  color: var(--color-deep-green);
  font-size: 14px;
  line-height: 1.35;
}

.student-list span {
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.35;
}

.student-list small {
  font-size: 12px;
  line-height: 1.35;
}

.student-pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  border-top: 1px solid var(--color-line);
  margin-top: 10px;
  padding-top: 12px;
  color: var(--color-muted);
  font-size: 13px;
}

.student-pager button {
  width: auto;
  margin: 0;
  border: 1px solid var(--color-border);
  padding: 5px 10px;
  background: #fff;
  color: var(--color-text);
  font-size: 12px;
}

.student-pager button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.profile-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 14px 0 0;
  border-top: 1px solid var(--color-line);
  padding-top: 12px;
}

.profile-list div {
  display: grid;
  gap: 4px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 9px 11px;
  background: var(--color-panel);
}

.profile-list dt,
.profile-list dd {
  margin: 0;
}

.profile-list dt {
  color: var(--color-muted);
  font-size: 13px;
}

.profile-list dd {
  color: var(--color-text);
  font-weight: 600;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.account-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.account-grid > div {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 14px;
  background: var(--color-panel);
}

.account-grid strong,
.account-grid span,
.account-grid small {
  display: block;
}

.file-grid {
  display: grid;
  gap: 8px;
}

.file-card {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 9px 10px;
  background: var(--color-panel);
}

.file-card:hover {
  border-color: rgba(0, 135, 60, 0.18);
  background: #fff;
}

.file-icon {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-academic-blue);
  font-size: 16px;
}

.file-icon.pdf {
  background: #fff5f5;
  color: #9f312f;
}

.file-icon.word {
  background: #eff6ff;
  color: #315f8f;
}

.file-icon.ppt {
  background: #fff7ed;
  color: #a65f2b;
}

.file-icon.image {
  background: var(--color-eco-green);
  color: var(--color-cau-green);
}

.file-main {
  min-width: 0;
}

.file-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-title-row strong {
  min-width: 0;
  overflow: hidden;
  color: var(--color-deep-green);
  font-size: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-title-row span {
  flex: 0 0 auto;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  padding: 1px 7px;
  background: #fff;
  color: var(--color-muted);
  font-size: 12px;
}

.file-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 3px;
}

.file-meta span {
  color: var(--color-muted);
  font-size: 12px;
}

.file-meta span + span::before {
  margin-right: 8px;
  color: var(--color-line);
  content: "/";
}

.file-card p {
  margin: 3px 0 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-primary-action,
.file-secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid rgba(0, 135, 60, 0.18);
  border-radius: var(--radius-sm);
  min-height: 28px;
  padding: 4px 8px;
  background: #fff;
  color: var(--color-cau-green);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.file-primary-action {
  background: var(--color-cau-green);
  color: #fff;
}

.file-primary-action:hover {
  color: #fff;
  background: #007234;
}

.file-secondary-action {
  border-color: var(--color-line);
  color: var(--color-muted);
  font-weight: 600;
}

.file-secondary-action:hover {
  border-color: rgba(0, 135, 60, 0.18);
  color: var(--color-cau-green);
}

.file-preview-note {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  background: #fff;
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.file-actions {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 6px;
  justify-content: flex-end;
}

.profile-form {
  display: grid;
}

.form-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.relation-note {
  display: grid;
  gap: 10px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 14px;
  background: var(--color-panel);
}

.relation-note strong {
  color: var(--color-deep-green);
}

.empty-note {
  color: var(--color-muted);
  font-size: 14px;
}

.file-input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 10px 11px;
  background: #fff;
}

.upload-file-note {
  display: block;
  margin-top: 8px;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
  word-break: break-all;
}

.upload-progress {
  display: grid;
  gap: 6px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: var(--color-soft-gray);
}

.upload-progress span {
  color: var(--color-muted);
  font-size: 13px;
}

.dialog-upload-progress {
  margin-bottom: 12px;
  text-align: left;
}

@media (max-width: 1280px) {
  .student-workspace {
    grid-template-columns: 260px minmax(0, 1fr);
  }

  .edit-panel {
    position: static;
    grid-column: 1 / -1;
    max-height: none;
  }
}

@media (max-width: 900px) {
  .student-heading,
  .student-workspace,
  .profile-list,
  .account-grid,
  .form-pair {
    grid-template-columns: 1fr;
  }

  .student-heading {
    display: grid;
  }

  .student-list {
    position: static;
    max-height: none;
  }

  .profile-heading {
    display: grid;
  }

  .profile-list div {
    grid-template-columns: 1fr;
    gap: 4px;
  }

  .file-card {
    grid-template-columns: 40px minmax(0, 1fr);
  }

  .file-actions {
    grid-column: 1 / -1;
    grid-template-columns: repeat(auto-fit, minmax(110px, max-content));
    justify-content: flex-start;
    justify-items: stretch;
  }
}
</style>


