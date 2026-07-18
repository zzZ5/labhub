<template>
  <InternalLayout title="成员管理">
    <section class="member-page">
      <LoadErrorNotice v-if="errorMessage" :description="errorMessage" :retrying="loading" @retry="reload" />

      <section class="member-grid">
        <article v-if="pendingUsers.length" class="card panel">
          <div class="panel-heading">
            <div>
              <h2>待审核账号</h2>
              <p>选择学校身份后通过审核；系统管理权限可在账号编辑中单独维护。</p>
            </div>
            <span>{{ pendingUsers.length }} 个</span>
          </div>
          <div class="review-list">
            <div v-for="user in pendingUsers" :key="user.id" class="review-card">
              <div><strong>{{ displayUser(user) }}</strong><span>{{ user.email || user.username }}</span></div>
              <el-select v-model="schoolIdentityForms[user.id]" placeholder="学校身份">
                <el-option v-for="item in schoolIdentityOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
              <div class="action-row">
                <el-button size="small" type="primary" :loading="savingId === user.id" @click="handleApprove(user)">通过</el-button>
                <el-button size="small" plain :loading="savingId === user.id" @click="handleReject(user)">暂不通过</el-button>
              </div>
            </div>
          </div>
        </article>

      </section>

      <article class="card panel account-panel">
        <div class="panel-heading account-toolbar">
          <div>
            <h2>全部成员</h2>
            <div class="account-summary-line">
              <p>共 {{ users.length }} 个账号<span v-if="studentMissingArchiveCount">，{{ studentMissingArchiveCount }} 名学生待建档</span></p>
              <el-popover placement="bottom-start" :width="420" trigger="click">
                <div class="permission-help-content">
                  <p>系统权限仅控制后台管理能力，与学校身份和成员状态分开维护。</p>
                  <dl>
                    <div><dt>网站编辑</dt><dd>维护门户内容、新闻和成果</dd></div>
                    <div><dt>资料管理员</dt><dd>维护内部资料库</dd></div>
                    <div><dt>仪器管理员</dt><dd>维护仪器信息和说明</dd></div>
                    <div><dt>系统管理员</dt><dd>管理账号和系统权限</dd></div>
                  </dl>
                </div>
                <template #reference><button class="permission-help-trigger" type="button">系统权限说明</button></template>
              </el-popover>
            </div>
          </div>
          <FilterToolbar has-filters>
            <template #primary><el-input v-model="keyword" clearable placeholder="搜索姓名、邮箱或账号" /></template>
            <template #filters>
              <el-select v-model="statusFilter" placeholder="状态"><el-option label="全部状态" value="all" /><el-option label="已审核" value="approved" /><el-option label="待审核" value="pending" /></el-select>
              <el-select v-model="membershipFilter" placeholder="成员状态"><el-option label="全部成员" value="all" /><el-option v-for="item in membershipStatusOptions" :key="item.value" :label="item.label" :value="item.value" /></el-select>
              <el-select v-model="schoolFilter" placeholder="学校身份"><el-option label="全部身份" value="all" /><el-option v-for="item in schoolIdentityOptions" :key="item.value" :label="item.label" :value="item.value" /></el-select>
              <el-select v-model="permissionFilter" placeholder="系统权限"><el-option label="全部权限" value="all" /><el-option v-for="role in systemPermissionRoles" :key="role.code" :label="roleLabel(role.code)" :value="role.code" /></el-select>
            </template>
            <template #actions>
              <el-button plain @click="openAccountImport">批量导入</el-button>
              <el-button plain :loading="loading" @click="reload">刷新</el-button>
              <el-button type="primary" @click="openCreateDrawer">新建账号</el-button>
            </template>
          </FilterToolbar>
        </div>

        <ListSkeleton v-if="loading && !users.length" :rows="8" thumbnail />
        <div v-else class="account-list">
          <article v-for="user in pagedUsers" :key="user.id" class="account-row-card">
            <div class="member-cell">
              <div class="account-avatar"><img v-if="user.profile?.avatar" :src="user.profile.avatar" :alt="displayUser(user)" /><span v-else>{{ initials(displayUser(user)) }}</span></div>
              <div><strong :title="displayUser(user)">{{ displayUser(user) }}</strong><small :title="user.email || user.username">{{ user.email || user.username }}</small></div>
            </div>
            <div class="compact-tags member-status-cell" data-label="状态与身份">
              <span :class="['status-tag', user.profile?.is_approved ? 'normal' : 'pending']">{{ user.profile?.is_approved ? '已审核' : '待审核' }}</span>
              <span :class="['status-tag', user.is_active ? 'normal' : 'rejected']">{{ user.is_active ? '可登录' : '已停用' }}</span>
              <span class="status-tag archived">{{ roleLabel(schoolIdentity(user)) }}</span>
              <span :class="['status-tag', membershipStatus(user) === 'active' ? 'normal' : 'archived']">{{ membershipStatusLabel(membershipStatus(user)) }}</span>
            </div>
            <div class="permission-chips compact-permissions" data-label="系统权限">
              <el-tooltip v-if="systemRoles(user).length" :content="systemRoles(user).map(roleLabel).join('、')" placement="top">
                <span class="status-tag archived">已分配 {{ systemRoles(user).length }} 项</span>
              </el-tooltip>
              <span v-else class="status-tag archived">无管理权限</span>
            </div>
            <div class="student-link-cell" data-label="学生档案"><RouterLink v-if="studentByUserId[user.id]" :to="{ path: '/students', query: { student: studentByUserId[user.id].id } }" class="student-link">{{ studentByUserId[user.id].name }}</RouterLink><button v-else-if="isStudentRole(user)" class="archive-create-button" type="button" :disabled="savingId === user.id" @click="handleCreateStudentArchive(user)">{{ savingId === user.id ? '生成中' : '生成档案' }}</button><span v-else class="status-tag archived">非学生</span></div>
            <div class="account-actions" data-label="账号操作">
              <el-button size="small" plain @click="openEditDrawer(user)">编辑</el-button>
              <ActionMenu :items="accountMenuItems(user)" @command="handleAccountMenu($event, user)" />
            </div>
          </article>
        </div>
        <EmptyState v-if="!loading && !filteredUsers.length" compact title="没有匹配成员" description="请调整搜索词或筛选条件。" />
        <AppPagination :page="memberPage" :total-pages="memberTotalPages" @change="memberPage = $event" />
      </article>

      <el-drawer v-model="accountDrawerVisible" class="entity-form-drawer" :title="editingUserId ? '编辑账号' : '新建账号'" size="min(520px, 100%)" destroy-on-close>
        <p class="entity-form-intro">维护登录信息、学校身份、成员状态和系统权限。</p>
        <el-form label-position="top" class="entity-form create-form">
          <el-form-item label="姓名"><el-input v-model="accountForm.real_name" placeholder="请输入成员姓名" /></el-form-item>
          <el-form-item label="头像">
            <ImageCropField v-model="accountForm.avatar" :existing-url="accountAvatarPreview" :existing-size="accountAvatarSize" :aspect-ratio="1" :output-width="800" :output-height="800" :max-size-mb="10" preview-shape="circle" @preview="accountAvatarPreview = $event" />
          </el-form-item>
          <el-form-item label="邮箱"><el-input v-model="accountForm.email" autocomplete="off" placeholder="用于登录和找回账号" /></el-form-item>
          <el-form-item label="账号名"><el-input v-model="accountForm.username" autocomplete="off" placeholder="可不填，默认使用邮箱" /></el-form-item>
          <el-form-item v-if="!editingUserId" label="初始密码"><el-input v-model="accountForm.password" type="password" autocomplete="new-password" show-password /></el-form-item>
          <el-form-item label="学校身份"><el-select v-model="accountForm.school_identity"><el-option v-for="item in schoolIdentityOptions" :key="item.value" :label="item.label" :value="item.value" /></el-select></el-form-item>
          <el-form-item label="成员状态"><el-segmented v-model="accountForm.membership_status" :options="membershipStatusOptions" /></el-form-item>
          <el-alert v-if="accountForm.membership_status !== 'active'" class="form-hint" type="info" :closable="false" title="历史成员的账号、学生档案和归档资料会继续保留，是否允许登录请单独设置。" />
          <el-form-item label="系统权限"><el-checkbox-group v-model="accountForm.system_roles"><el-checkbox v-for="role in systemPermissionOptions" :key="role.value" :label="role.value">{{ role.label }}</el-checkbox></el-checkbox-group></el-form-item>
          <el-form-item label="账号状态"><el-switch v-model="accountForm.is_approved" active-text="已审核" inactive-text="待审核" /></el-form-item>
          <el-form-item v-if="editingUserId" label="登录状态"><el-switch v-model="accountForm.is_active" active-text="启用" inactive-text="停用" /></el-form-item>
        </el-form>
        <template #footer><div class="entity-form-footer"><el-button @click="accountDrawerVisible = false">取消</el-button><el-button type="primary" :loading="accountSaving" @click="submitAccountForm">{{ editingUserId ? '保存修改' : '创建账号' }}</el-button></div></template>
      </el-drawer>

      <AccountImportDialog
        v-model:open="accountImportVisible"
        :saving="accountImporting"
        :progress="accountImportProgress"
        :result="accountImportResult"
        @import="handleAccountImport"
      />

      <el-dialog v-model="passwordVisible" title="重置密码" width="420px">
        <el-alert class="password-alert" type="warning" :closable="false" title="保存后旧密码立即失效，请通过线下方式把新密码告知成员。" />
        <el-form label-position="top"><el-form-item label="成员"><el-input :model-value="passwordTargetName" disabled /></el-form-item><el-form-item label="新密码"><el-input v-model="passwordForm.password" type="password" autocomplete="new-password" show-password /></el-form-item></el-form>
        <template #footer><el-button @click="passwordVisible = false">取消</el-button><el-button type="primary" :loading="passwordSaving" @click="submitPasswordReset">保存新密码</el-button></template>
      </el-dialog>
    </section>
  </InternalLayout>
</template>
<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  approveUser,
  assignUserRole,
  createUser,
  deleteUser,
  fetchPendingUsers,
  fetchRoles,
  fetchUsers,
  importAccountsExcel,
  removeUserRole,
  resetUserPassword,
  type AccountImportResult,
  type CurrentUser,
  type Role,
  updateUser,
} from '../../api/accounts'
import { createStudentProfile, fetchStudentProfiles, type StudentProfile } from '../../api/students'
import AppPagination from '../../components/AppPagination.vue'
import ActionMenu, { type ActionMenuItem } from '../../components/ActionMenu.vue'
import FilterToolbar from '../../components/FilterToolbar.vue'
import ImageCropField from '../../components/ImageCropField.vue'
import LoadErrorNotice from '../../components/LoadErrorNotice.vue'
import ListSkeleton from '../../components/ListSkeleton.vue'
import EmptyState from '../../components/EmptyState.vue'
import { useListPagination } from '../../composables/useListPagination'
import { useDebouncedValue } from '../../composables/useDebouncedValue'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { useSessionStore } from '../../stores/session'
import AccountImportDialog from './components/AccountImportDialog.vue'

const session = useSessionStore()
const users = ref<CurrentUser[]>([])
const pendingUsers = ref<CurrentUser[]>([])
const roles = ref<Role[]>([])
const studentProfiles = ref<StudentProfile[]>([])
const loading = ref(false)
const savingId = ref<number | null>(null)
const accountDrawerVisible = ref(false)
const accountSaving = ref(false)
const accountImportVisible = ref(false)
const accountImporting = ref(false)
const accountImportProgress = ref(0)
const accountImportResult = ref<AccountImportResult | null>(null)
const editingUserId = ref<number | null>(null)
const passwordVisible = ref(false)
const passwordSaving = ref(false)
const passwordTarget = ref<CurrentUser | null>(null)
const accountAvatarPreview = ref('')
const accountAvatarSize = computed(() => users.value.find((user) => user.id === editingUserId.value)?.profile?.avatar_size || 0)
const errorMessage = ref('')
const keyword = ref('')
const debouncedKeyword = useDebouncedValue(keyword)
const statusFilter = ref('all')
const schoolFilter = ref('all')
const permissionFilter = ref('all')
const membershipFilter = ref('all')
const memberPage = ref(1)
const schoolIdentityForms = reactive<Record<number, string>>({})
const accountForm = reactive({
  real_name: '',
  email: '',
  username: '',
  password: '',
  school_identity: 'other',
  membership_status: 'active',
  avatar: undefined as File | undefined,
  is_approved: true,
  is_active: true,
  system_roles: [] as string[],
  phone: '',
})
const passwordForm = reactive({
  password: '',
})

const schoolIdentityOptions = [
  { value: 'pi', label: '硕博导师' },
  { value: 'postdoc', label: '博士后' },
  { value: 'phd', label: '博士生' },
  { value: 'master', label: '硕士生' },
  { value: 'undergraduate', label: '本科生' },
  { value: 'other', label: '其他成员' },
]

const membershipStatusOptions = [
  { value: 'active', label: '在组' },
  { value: 'former', label: '已毕业/离组' },
]

const systemPermissionOptions = [
  { value: 'editor', label: '网站编辑' },
  { value: 'document_manager', label: '资料管理员' },
  { value: 'instrument_manager', label: '仪器管理员' },
  { value: 'admin', label: '系统管理员' },
]

const schoolIdentityCodes = schoolIdentityOptions.map((item) => item.value)
const systemPermissionCodes = systemPermissionOptions.map((item) => item.value)
const allRoleOptions = [...schoolIdentityOptions, ...systemPermissionOptions]

const fallbackRoles: Role[] = allRoleOptions.map((item, index) => ({
  id: index + 1,
  name: item.label,
  code: item.value,
  description: roleDescription(item.value),
  is_system: true,
  created_at: '',
}))

const normalizedRoles = computed(() => {
  const source = roles.value.length ? roles.value : fallbackRoles
  const known = new Set(source.map((role) => role.code))
  const missing = fallbackRoles.filter((role) => !known.has(role.code))
  return [...source, ...missing].sort((a, b) => roleOrder(a.code) - roleOrder(b.code))
})
const systemPermissionRoles = computed(() => normalizedRoles.value.filter((role) => systemPermissionCodes.includes(role.code)))
const studentByUserId = computed<Record<number, StudentProfile>>(() =>
  Object.fromEntries(studentProfiles.value.map((student) => [student.user, student])),
)
const studentMissingArchiveCount = computed(
  () => users.value.filter((user) => isStudentRole(user) && !studentByUserId.value[user.id]).length,
)
const filteredUsers = computed(() => {
  const term = debouncedKeyword.value.trim().toLowerCase()
  return users.value.filter((user) => {
    const text = `${displayUser(user)} ${user.email} ${user.username}`.toLowerCase()
    const statusMatched =
      statusFilter.value === 'all' ||
      (statusFilter.value === 'approved' && user.profile?.is_approved) ||
      (statusFilter.value === 'pending' && !user.profile?.is_approved)
    const schoolMatched = schoolFilter.value === 'all' || schoolIdentity(user) === schoolFilter.value
    const membershipMatched = membershipFilter.value === 'all' || membershipStatus(user) === membershipFilter.value
    const permissionMatched = permissionFilter.value === 'all' || systemRoles(user).includes(permissionFilter.value)
    return (!term || text.includes(term)) && statusMatched && schoolMatched && membershipMatched && permissionMatched
  })
})
const filteredUserTotal = computed(() => filteredUsers.value.length)
const { totalPages: memberTotalPages, paginate: paginateMembers } = useListPagination(filteredUserTotal, { page: memberPage })
const pagedUsers = computed(() => paginateMembers(filteredUsers.value))
const passwordTargetName = computed(() => (passwordTarget.value ? displayUser(passwordTarget.value) : ''))

function roleOrder(code: string) {
  const order = [...schoolIdentityCodes, ...systemPermissionCodes].indexOf(code)
  return order >= 0 ? order : 999
}

function displayUser(user: CurrentUser) {
  return studentByUserId.value[user.id]?.name || user.profile?.real_name || user.first_name || user.username
}

function initials(value: string) {
  return value.trim().slice(0, 1) || '员'
}

function roleLabel(code: string) {
  return allRoleOptions.find((item) => item.value === code)?.label || code
}

function roleDescription(code: string) {
  const descriptions: Record<string, string> = {
    undergraduate: '本科生身份，可维护本人学生档案和归档资料。',
    master: '硕士生身份，可维护本人学生档案和归档资料。',
    phd: '博士生身份，可维护本人学生档案和归档资料。',
    postdoc: '博士后身份，可访问成员内部资料和科研管理信息。',
    pi: '硕博导师，可查看所指导学生的档案，不自动获得后台管理权限。',
    other: '其他学校身份，用于人员分类。',
    editor: '维护门户内容、新闻、成员展示和科研成果。',
    document_manager: '上传、维护和归档内部资料。',
    instrument_manager: '维护仪器平台的设备信息、图片和使用说明。',
    admin: '系统管理员，可管理账号、角色和核心配置。',
  }
  return descriptions[code] || '系统角色。'
}

function displayRoles(user: CurrentUser) {
  if (user.is_superuser) return Array.from(new Set(['admin', ...user.roles]))
  return user.roles
}

function schoolIdentity(user: CurrentUser) {
  const profileIdentity = user.profile?.school_identity
  if (schoolIdentityCodes.includes(profileIdentity)) return profileIdentity
  return 'other'
}

function membershipStatus(user: CurrentUser) {
  return user.profile?.membership_status || 'active'
}

function membershipStatusLabel(status: string) {
  return membershipStatusOptions.find((item) => item.value === status)?.label || status
}

function systemRoles(user: CurrentUser) {
  return displayRoles(user).filter((role) => systemPermissionCodes.includes(role))
}

function isStudentRole(user: CurrentUser) {
  return ['undergraduate', 'master', 'phd'].includes(schoolIdentity(user))
}

function studentDegreeType(user: CurrentUser) {
  const identity = schoolIdentity(user)
  return ['undergraduate', 'master', 'phd'].includes(identity) ? identity : 'master'
}

function syncForms() {
  users.value.forEach((user) => {
    schoolIdentityForms[user.id] = schoolIdentity(user)
  })
  pendingUsers.value.forEach((user) => {
    schoolIdentityForms[user.id] = schoolIdentity(user)
  })
}

function resetAccountForm() {
  editingUserId.value = null
  accountForm.real_name = ''
  accountForm.email = ''
  accountForm.username = ''
  accountForm.password = ''
  accountForm.school_identity = 'other'
  accountForm.membership_status = 'active'
  accountForm.avatar = undefined
  accountAvatarPreview.value = ''
  accountForm.is_approved = true
  accountForm.is_active = true
  accountForm.system_roles = []
  accountForm.phone = ''
}

function openCreateDrawer() {
  resetAccountForm()
  accountDrawerVisible.value = true
}

function openAccountImport() {
  accountImportProgress.value = 0
  accountImportResult.value = null
  accountImportVisible.value = true
}

async function handleAccountImport(file: File) {
  if (!file.name.toLowerCase().endsWith('.xlsx')) {
    ElMessage.warning('请选择 .xlsx 账号清单。')
    return
  }
  accountImporting.value = true
  accountImportProgress.value = 0
  accountImportResult.value = null
  try {
    const result = await importAccountsExcel(file, (event) => {
      if (event.total) accountImportProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    accountImportProgress.value = 100
    accountImportResult.value = result
    const message = result.failed
      ? `导入完成：新增 ${result.created} 个，${result.failed} 行失败。`
      : `已新增 ${result.created} 个账号，生成 ${result.student_profiles} 个学生档案。`
    result.failed ? ElMessage.warning(message) : ElMessage.success(message)
    await reload()
    memberPage.value = 1
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '导入失败，请确认模板列名和账号内容。')
  } finally {
    accountImporting.value = false
    setTimeout(() => {
      if (!accountImporting.value) accountImportProgress.value = 0
    }, 900)
  }
}

function openEditDrawer(user: CurrentUser) {
  editingUserId.value = user.id
  accountForm.real_name = displayUser(user)
  accountForm.email = user.email || ''
  accountForm.username = user.username || ''
  accountForm.password = ''
  accountForm.school_identity = schoolIdentity(user)
  accountForm.membership_status = membershipStatus(user)
  accountForm.avatar = undefined
  accountAvatarPreview.value = user.profile?.avatar || ''
  accountForm.is_approved = Boolean(user.profile?.is_approved)
  accountForm.is_active = Boolean(user.is_active)
  accountForm.system_roles = systemRoles(user)
  accountForm.phone = user.profile?.phone || ''
  accountDrawerVisible.value = true
}

function openPasswordDialog(user: CurrentUser) {
  passwordTarget.value = user
  passwordForm.password = ''
  passwordVisible.value = true
}

function handleAccountMenu(command: string, user: CurrentUser) {
  if (command === 'password') {
    openPasswordDialog(user)
    return
  }
  if (command === 'delete') void confirmDeleteAccount(user)
}

function accountMenuItems(user: CurrentUser): ActionMenuItem[] {
  const items: ActionMenuItem[] = [{ command: 'password', label: '重置密码' }]
  if (user.id !== session.user?.id && !user.is_superuser) {
    items.push({ command: 'delete', label: '删除账号', divided: true, danger: true })
  }
  return items
}

async function submitAccountForm() {
  if (!accountForm.email.trim()) {
    ElMessage.warning('请填写邮箱。')
    return
  }
  if (!editingUserId.value && !accountForm.password) {
    ElMessage.warning('请填写初始密码。')
    return
  }
  accountSaving.value = true
  try {
    if (editingUserId.value) {
      const currentUser = users.value.find((user) => user.id === editingUserId.value)
      const previousSystemRoles = currentUser ? systemRoles(currentUser) : []
      await updateUser(editingUserId.value, {
        email: accountForm.email.trim(),
        username: accountForm.username.trim(),
        real_name: accountForm.real_name.trim(),
        phone: accountForm.phone.trim(),
        school_identity: accountForm.school_identity,
        membership_status: accountForm.membership_status,
        avatar: accountForm.avatar,
        is_approved: accountForm.is_approved,
        is_active: accountForm.is_active,
      })
      const nextSystemRoles = new Set(accountForm.system_roles)
      await Promise.all(previousSystemRoles.filter((role) => !nextSystemRoles.has(role)).map((role) => removeUserRole(editingUserId.value!, role)))
      await Promise.all(accountForm.system_roles.filter((role) => !previousSystemRoles.includes(role)).map((role) => assignUserRole(editingUserId.value!, role)))
      if (currentUser && accountForm.membership_status !== 'active' && studentByUserId.value[currentUser.id]) {
        ElMessage.info('该成员的学生档案和归档资料已保留，可在学生档案中继续查看。')
      }
      ElMessage.success('成员账号已保存。')
    } else {
      await createUser({
        email: accountForm.email.trim(),
        username: accountForm.username.trim(),
        password: accountForm.password,
        real_name: accountForm.real_name.trim(),
        phone: accountForm.phone.trim(),
        school_identity: accountForm.school_identity,
        membership_status: accountForm.membership_status,
        avatar: accountForm.avatar,
        is_approved: accountForm.is_approved,
        system_roles: accountForm.system_roles,
      })
      ElMessage.success('成员账号已创建。')
    }
    accountDrawerVisible.value = false
    await reload()
  } catch (error: any) {
    const data = error?.response?.data || {}
    const firstError = Object.values(data).flat?.()[0]
    ElMessage.error(String(firstError || data.detail || '账号保存失败，请检查邮箱、密码或权限设置。'))
  } finally {
    accountSaving.value = false
  }
}

async function submitPasswordReset() {
  if (!passwordTarget.value) return
  if (!passwordForm.password) {
    ElMessage.warning('请填写新密码。')
    return
  }
  passwordSaving.value = true
  try {
    await resetUserPassword(passwordTarget.value.id, passwordForm.password)
    ElMessage.success('密码已重置。')
    passwordVisible.value = false
  } catch (error: any) {
    const data = error?.response?.data || {}
    const firstError = Object.values(data).flat?.()[0]
    ElMessage.error(String(firstError || data.detail || '密码重置失败。'))
  } finally {
    passwordSaving.value = false
  }
}

async function handleCreateStudentArchive(user: CurrentUser) {
  if (studentByUserId.value[user.id]) {
    ElMessage.info('该账号已经有学生档案。')
    return
  }
  if (!isStudentRole(user)) {
    ElMessage.warning('只有本科生、硕士生或博士生账号可以生成学生档案。')
    return
  }
  savingId.value = user.id
  try {
    const profile = await createStudentProfile({
      user: user.id,
      name: displayUser(user),
      degree_type: studentDegreeType(user),
      grade: '',
    })
    ElMessage.success(`已生成“${profile.name}”的学生档案。`)
    await reload()
  } catch (error: any) {
    const data = error?.response?.data || {}
    const firstError = Object.values(data).flat?.()[0]
    ElMessage.error(String(firstError || data.detail || '学生档案生成失败，请确认账号身份或是否已建档。'))
  } finally {
    savingId.value = null
  }
}

async function confirmDeleteAccount(user: CurrentUser) {
  const archivedStudent = studentByUserId.value[user.id]
  const extra = archivedStudent ? `\n该账号已绑定学生档案“${archivedStudent.name}”，删除账号会一并删除对应学生档案和归档资料。` : ''
  try {
    await ElMessageBox.confirm(`确定删除账号“${displayUser(user)}”吗？${extra}`, '删除成员账号', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    await deleteUser(user.id)
    ElMessage.success('成员账号已删除。')
    await reload()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '删除失败，请确认权限。')
  }
}

async function reload() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [roleData, userData, pendingData, studentData] = await Promise.all([
      fetchRoles(),
      fetchUsers(),
      fetchPendingUsers(),
      fetchStudentProfiles(),
    ])
    roles.value = roleData
    users.value = userData
    pendingUsers.value = pendingData
    studentProfiles.value = studentData
    syncForms()
    clampMemberPage()
  } catch (error: any) {
    users.value = []
    pendingUsers.value = []
    roles.value = []
    studentProfiles.value = []
    errorMessage.value =
      error?.response?.status === 403
        ? '当前账号没有成员管理权限，请使用系统管理员账号访问。'
        : '成员数据加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

function clampMemberPage() {
  if (memberPage.value > memberTotalPages.value) memberPage.value = memberTotalPages.value
  if (memberPage.value < 1) memberPage.value = 1
}

async function handleApprove(user: CurrentUser) {
  savingId.value = user.id
  try {
    const identity = schoolIdentityForms[user.id] || 'other'
    await approveUser(user.id, { is_approved: true, school_identity: identity })
    ElMessage.success('账号已通过审核，学校身份已保存。')
    await reload()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '审核失败，请稍后重试。')
  } finally {
    savingId.value = null
  }
}

async function handleReject(user: CurrentUser) {
  savingId.value = user.id
  try {
    await approveUser(user.id, { is_approved: false, school_identity: schoolIdentityForms[user.id] || 'other' })
    ElMessage.success('账号已标记为暂不通过。')
    await reload()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '操作失败，请稍后重试。')
  } finally {
    savingId.value = null
  }
}

onMounted(reload)

watch([debouncedKeyword, statusFilter, membershipFilter, schoolFilter, permissionFilter], () => {
  memberPage.value = 1
})

</script>

<style scoped>
.member-page {
  display: grid;
  gap: 14px;
}

.heading-actions,
.action-row,
.assign-cell,
.filters,
.identity-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.permission-alert {
  border-radius: var(--radius-md);
}

.panel:hover {
  transform: none;
}

.member-grid {
  display: grid;
  gap: 12px;
}

.panel {
  padding: 24px;
  border-radius: var(--radius-lg);
}

.account-summary-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 12px;
}

.permission-help-trigger {
  border: 0;
  border-bottom: 1px solid rgba(0, 135, 60, 0.3);
  padding: 0;
  background: transparent;
  color: var(--color-cau-green);
  cursor: pointer;
  font: inherit;
  font-size: 13px;
  font-weight: 650;
}

.permission-help-content > p {
  margin: 0 0 10px;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
}

.permission-help-content dl {
  display: grid;
  gap: 7px;
  margin: 0;
}

.permission-help-content dl div {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr);
  gap: 10px;
}

.permission-help-content dt,
.permission-help-content dd {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
}

.permission-help-content dt {
  color: var(--color-deep-green);
  font-weight: 700;
}

.permission-help-content dd {
  color: var(--color-muted);
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 12px;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 20px;
  font-weight: 650;
}

.panel-heading p,
.panel-heading span,
.review-card span,
.member-cell small {
  margin: 4px 0 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

.review-list,
.review-card {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 14px;
  background: var(--color-panel);
}

.review-card {
  display: grid;
  grid-template-columns: 1fr 170px auto;
  align-items: center;
  gap: 12px;
}

.review-card strong,
.review-card span,
.member-cell strong,
.member-cell small {
  display: block;
}

.member-cell,
.avatar-editor {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 0;
}

.member-cell > div:last-child { min-width: 0; }

.member-cell strong,
.member-cell small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-avatar {
  display: grid;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  place-items: center;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: 50%;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-weight: 700;
}

.account-avatar.large {
  flex-basis: 66px;
  width: 66px;
  height: 66px;
  font-size: 20px;
}

.account-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-upload {
  border: 1px solid rgba(0, 135, 60, 0.24);
  border-radius: var(--radius-sm);
  padding: 7px 12px;
  color: var(--color-cau-green);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.avatar-upload input {
  display: none;
}

.field-note {
  color: var(--color-muted);
  font-size: 12px;
}

.account-panel {
  overflow: hidden;
}

.account-toolbar {
  display: grid;
  grid-template-columns: 1fr;
  align-items: center;
}

.account-toolbar :deep(.filter-toolbar) {
  width: 100%;
}

.filters {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.filters .el-input {
  width: 220px;
}

.filters .el-select {
  width: 128px;
}

.account-list {
  display: grid;
  gap: 12px;
}

.account-row-card {
  display: grid;
  grid-template-columns: minmax(170px, 1.1fr) minmax(220px, 1.35fr) minmax(150px, 1fr) 104px 118px;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  background: var(--color-panel);
  min-width: 0;
}

.account-row-card:hover {
  border-color: rgba(0, 135, 60, 0.18);
  background: #fff;
}

.compact-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.identity-cell .el-select,
.assign-cell .el-select {
  min-width: 132px;
}

.account-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.permission-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.compact-permissions {
  min-width: 0;
}

.student-link-cell {
  display: flex;
  align-items: center;
}

.student-link {
  max-width: 100%;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.18);
  border-radius: 999px;
  padding: 5px 10px;
  background: var(--color-eco-green);
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archive-create-button {
  border: 1px solid rgba(0, 135, 60, 0.22);
  border-radius: 999px;
  padding: 5px 10px;
  background: #fff;
  color: var(--color-cau-green);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.archive-create-button:hover:not(:disabled) {
  background: var(--color-eco-green);
}

.archive-create-button:disabled {
  cursor: progress;
  opacity: 0.62;
}

.create-form {
  display: grid;
}

.create-form .el-select,
.create-form .el-input {
  width: 100%;
}

.create-form :deep(.el-checkbox-group) {
  display: grid;
  gap: 8px;
}

.password-alert {
  margin-bottom: 16px;
}

.form-hint {
  margin: 0 0 18px;
  border-radius: var(--radius-sm);
}

@media (max-width: 1180px) {
  .account-row-card {
    grid-template-columns: minmax(210px, 1.2fr) minmax(0, 1fr) minmax(130px, .7fr);
  }

  .student-link-cell { grid-column: 1 / 2; }
  .account-actions { grid-column: 2 / -1; }
  .account-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 980px) {
  .account-toolbar {
    display: grid;
  }

  .member-grid {
    grid-template-columns: 1fr;
  }

}

@media (max-width: 720px) {
  .member-grid,
  .review-card {
    grid-template-columns: 1fr;
  }

  .heading-actions,
  .filters {
    justify-content: flex-start;
  }

  .account-panel { padding: 14px; }
  .account-row-card {
    grid-template-columns: 1fr 1fr;
    gap: 12px 14px;
    padding: 14px;
  }

  .member-cell,
  .member-status-cell {
    grid-column: 1 / -1;
  }

  .member-cell { padding-bottom: 10px; border-bottom: 1px solid var(--color-line); }
  .member-status-cell { gap: 6px; }
  .compact-permissions,
  .student-link-cell,
  .account-actions { display: flex; grid-column: auto; align-items: center; min-width: 0; }
  .account-actions { justify-content: flex-end; }
  .compact-permissions::before,
  .student-link-cell::before,
  .account-actions::before {
    display: block;
    margin-right: auto;
    color: var(--color-muted);
    content: attr(data-label);
    font-size: 12px;
  }

  .compact-permissions,
  .student-link-cell { grid-column: 1 / -1; }
  .account-actions { grid-column: 1 / -1; border-top: 1px solid var(--color-line); padding-top: 10px; }

}
</style>





