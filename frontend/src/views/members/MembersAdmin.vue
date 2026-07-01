<template>
  <InternalLayout title="成员管理">
    <section class="member-page">
      <header class="surface-heading member-heading">
        <div>
          <span>账号、学校身份与系统权限</span>
          <h1>成员账号管理</h1>
          <p>账号状态决定能否进入内部平台；学校身份表示他在课题组/学校中的身份；系统权限只表示他在平台里能管理哪些功能。</p>
        </div>
        <div class="heading-actions">
          <el-button plain @click="openCreateDrawer">新建账号</el-button>
          <el-button type="primary" :loading="loading" @click="reload">刷新</el-button>
        </div>
      </header>

      <el-alert
        v-if="errorMessage"
        class="permission-alert"
        type="warning"
        :closable="false"
        :title="errorMessage"
      />

      <section class="stat-grid">
        <article class="card stat-card">
          <span>全部账号</span>
          <strong>{{ users.length }}</strong>
        </article>
        <article class="card stat-card">
          <span>已审核</span>
          <strong>{{ approvedCount }}</strong>
        </article>
        <article class="card stat-card">
          <span>待审核</span>
          <strong>{{ pendingUsers.length }}</strong>
        </article>
        <article class="card stat-card">
          <span>学生待建档</span>
          <strong>{{ studentMissingArchiveCount }}</strong>
        </article>
      </section>

      <section class="member-grid">
        <article class="card panel">
          <div class="panel-heading">
            <div>
              <h2>待审核账号</h2>
              <p>选择学校身份后通过审核。系统管理权限可在下方单独添加。</p>
            </div>
            <span>{{ pendingUsers.length }} 个</span>
          </div>
          <div v-if="pendingUsers.length" class="review-list">
            <div v-for="user in pendingUsers" :key="user.id" class="review-card">
              <div>
                <strong>{{ displayUser(user) }}</strong>
                <span>{{ user.email || user.username }}</span>
              </div>
              <el-select v-model="schoolIdentityForms[user.id]" placeholder="学校身份">
                <el-option v-for="item in schoolIdentityOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
              <div class="action-row">
                <el-button size="small" type="primary" :loading="savingId === user.id" @click="handleApprove(user)">通过</el-button>
                <el-button size="small" plain :loading="savingId === user.id" @click="handleReject(user)">暂不通过</el-button>
              </div>
            </div>
          </div>
          <div v-else class="empty-note">暂无待审核账号。</div>
        </article>

        <article class="card panel permission-note">
          <strong>系统权限</strong>
          <p>系统权限只控制后台管理能力，和学校身份分开维护。</p>
          <div class="permission-summary">
            <span><b>网站编辑</b>维护门户内容、新闻和成果</span>
            <span><b>资料管理员</b>维护内部资料库</span>
            <span><b>仪器管理员</b>维护仪器信息和说明</span>
            <span><b>系统管理员</b>管理账号和系统权限</span>
          </div>
        </article>
      </section>

      <article class="card panel account-panel">
        <div class="panel-heading account-toolbar">
          <div>
            <h2>全部成员</h2>
            <p>学校身份负责人员分类；系统权限负责后台管理能力。学生档案绑定在“学生档案”页面完成。</p>
          </div>
          <div class="filters">
            <el-input v-model="keyword" clearable placeholder="搜索姓名、邮箱或账号" />
            <el-select v-model="statusFilter" placeholder="状态">
              <el-option label="全部状态" value="all" />
              <el-option label="已审核" value="approved" />
              <el-option label="待审核" value="pending" />
            </el-select>
            <el-select v-model="schoolFilter" placeholder="学校身份">
              <el-option label="全部身份" value="all" />
              <el-option v-for="item in schoolIdentityOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-select v-model="permissionFilter" placeholder="系统权限">
              <el-option label="全部权限" value="all" />
              <el-option v-for="role in systemPermissionRoles" :key="role.code" :label="roleLabel(role.code)" :value="role.code" />
            </el-select>
          </div>
        </div>

        <div class="account-list">
          <article v-for="user in filteredUsers" :key="user.id" class="account-row-card">
            <div class="member-cell">
              <strong>{{ displayUser(user) }}</strong>
              <small>{{ user.email || user.username }}</small>
            </div>
            <div class="compact-tags">
              <span :class="['status-tag', user.profile?.is_approved ? 'normal' : 'pending']">
                {{ user.profile?.is_approved ? '已审核' : '待审核' }}
              </span>
              <span :class="['status-tag', user.is_active ? 'normal' : 'rejected']">
                {{ user.is_active ? '可登录' : '已停用' }}
              </span>
              <span class="status-tag archived">{{ roleLabel(schoolIdentity(user)) }}</span>
            </div>
            <div class="permission-chips compact-permissions">
              <span v-for="role in systemRoles(user)" :key="role" class="status-tag archived">{{ roleLabel(role) }}</span>
              <span v-if="!systemRoles(user).length" class="status-tag archived">普通权限</span>
            </div>
            <div class="student-link-cell">
              <RouterLink v-if="studentByUserId[user.id]" to="/students" class="student-link">
                {{ studentByUserId[user.id].name }}
              </RouterLink>
              <RouterLink v-else-if="isStudentRole(user)" to="/students" class="status-tag pending">待建档</RouterLink>
              <span v-else class="status-tag archived">非学生</span>
            </div>
            <div class="account-actions">
              <el-button size="small" plain @click="openEditDrawer(user)">编辑</el-button>
              <el-button size="small" plain @click="openPasswordDialog(user)">重置密码</el-button>
              <el-button
                v-if="user.id !== session.user?.id && !user.is_superuser"
                size="small"
                plain
                type="danger"
                @click="confirmDeleteAccount(user)"
              >
                删除
              </el-button>
            </div>
          </article>
        </div>
        <div v-if="!filteredUsers.length" class="empty-note">没有符合条件的成员。</div>
      </article>

      <el-drawer v-model="accountDrawerVisible" :title="editingUserId ? '编辑成员账号' : '新建成员账号'" size="440px">
        <el-form label-position="top" class="create-form">
          <el-form-item label="姓名">
            <el-input v-model="accountForm.real_name" placeholder="请输入成员姓名" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="accountForm.email" autocomplete="off" placeholder="用于登录和找回账号" />
          </el-form-item>
          <el-form-item label="账号名">
            <el-input v-model="accountForm.username" autocomplete="off" placeholder="可不填，默认使用邮箱" />
          </el-form-item>
          <el-form-item v-if="!editingUserId" label="初始密码">
            <el-input v-model="accountForm.password" type="password" autocomplete="new-password" show-password />
          </el-form-item>
          <el-form-item label="学校身份">
            <el-select v-model="accountForm.role_type">
              <el-option v-for="item in schoolIdentityOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="系统权限">
            <el-checkbox-group v-model="accountForm.system_roles">
              <el-checkbox v-for="role in systemPermissionOptions" :key="role.value" :label="role.value">
                {{ role.label }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="账号状态">
            <el-switch
              v-model="accountForm.is_approved"
              active-text="已审核"
              inactive-text="待审核"
            />
          </el-form-item>
          <el-form-item v-if="editingUserId" label="登录状态">
            <el-switch
              v-model="accountForm.is_active"
              active-text="启用"
              inactive-text="停用"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="drawer-footer">
            <el-button @click="accountDrawerVisible = false">取消</el-button>
            <el-button type="primary" :loading="accountSaving" @click="submitAccountForm">
              {{ editingUserId ? '保存账号' : '创建账号' }}
            </el-button>
          </div>
        </template>
      </el-drawer>

      <el-dialog v-model="passwordVisible" title="重置密码" width="420px">
        <el-alert
          class="password-alert"
          type="warning"
          :closable="false"
          title="保存后旧密码立即失效，请通过线下方式把新密码告知成员。"
        />
        <el-form label-position="top">
          <el-form-item label="成员">
            <el-input :model-value="passwordTargetName" disabled />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="passwordForm.password" type="password" autocomplete="new-password" show-password />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="passwordVisible = false">取消</el-button>
          <el-button type="primary" :loading="passwordSaving" @click="submitPasswordReset">保存新密码</el-button>
        </template>
      </el-dialog>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  approveUser,
  assignUserRole,
  createUser,
  deleteUser,
  fetchPendingUsers,
  fetchRoles,
  fetchUsers,
  removeUserRole,
  resetUserPassword,
  type CurrentUser,
  type Role,
  updateUser,
} from '../../api/accounts'
import { fetchStudentProfiles, type StudentProfile } from '../../api/students'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { useSessionStore } from '../../stores/session'

const session = useSessionStore()
const users = ref<CurrentUser[]>([])
const pendingUsers = ref<CurrentUser[]>([])
const roles = ref<Role[]>([])
const studentProfiles = ref<StudentProfile[]>([])
const loading = ref(false)
const savingId = ref<number | null>(null)
const accountDrawerVisible = ref(false)
const accountSaving = ref(false)
const editingUserId = ref<number | null>(null)
const passwordVisible = ref(false)
const passwordSaving = ref(false)
const passwordTarget = ref<CurrentUser | null>(null)
const errorMessage = ref('')
const keyword = ref('')
const statusFilter = ref('all')
const schoolFilter = ref('all')
const permissionFilter = ref('all')
const schoolIdentityForms = reactive<Record<number, string>>({})
const assignRoles = reactive<Record<number, string>>({})
const accountForm = reactive({
  real_name: '',
  email: '',
  username: '',
  password: '',
  role_type: 'member',
  is_approved: true,
  is_active: true,
  system_roles: [] as string[],
  phone: '',
})
const passwordForm = reactive({
  password: '',
})

const schoolIdentityOptions = [
  { value: 'member', label: '课题组成员' },
  { value: 'master', label: '硕士生' },
  { value: 'phd', label: '博士生' },
  { value: 'postdoc', label: '博士后' },
  { value: 'pi', label: '硕博导师' },
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
const approvedCount = computed(() => users.value.filter((user) => user.profile?.is_approved).length)
const studentByUserId = computed<Record<number, StudentProfile>>(() =>
  Object.fromEntries(studentProfiles.value.map((student) => [student.user, student])),
)
const studentMissingArchiveCount = computed(
  () => users.value.filter((user) => isStudentRole(user) && !studentByUserId.value[user.id]).length,
)
const filteredUsers = computed(() => {
  const term = keyword.value.trim().toLowerCase()
  return users.value.filter((user) => {
    const text = `${displayUser(user)} ${user.email} ${user.username}`.toLowerCase()
    const statusMatched =
      statusFilter.value === 'all' ||
      (statusFilter.value === 'approved' && user.profile?.is_approved) ||
      (statusFilter.value === 'pending' && !user.profile?.is_approved)
    const schoolMatched = schoolFilter.value === 'all' || schoolIdentity(user) === schoolFilter.value
    const permissionMatched = permissionFilter.value === 'all' || systemRoles(user).includes(permissionFilter.value)
    return (!term || text.includes(term)) && statusMatched && schoolMatched && permissionMatched
  })
})
const passwordTargetName = computed(() => (passwordTarget.value ? displayUser(passwordTarget.value) : ''))

function roleOrder(code: string) {
  const order = [...schoolIdentityCodes, ...systemPermissionCodes].indexOf(code)
  return order >= 0 ? order : 999
}

function displayUser(user: CurrentUser) {
  return studentByUserId.value[user.id]?.name || user.profile?.real_name || user.first_name || user.username
}

function roleLabel(code: string) {
  return allRoleOptions.find((item) => item.value === code)?.label || code
}

function roleDescription(code: string) {
  const descriptions: Record<string, string> = {
    member: '普通内部成员，可访问基础内部资料。',
    master: '硕士生身份，可维护本人学生档案和归档资料。',
    phd: '博士生身份，可维护本人学生档案和归档资料。',
    postdoc: '博士后身份，可访问成员内部资料和科研管理信息。',
    pi: '硕博导师，可查看和管理学生档案。',
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
  const profileIdentity = user.profile?.role_type
  if (schoolIdentityCodes.includes(profileIdentity)) return profileIdentity
  return displayRoles(user).find((role) => schoolIdentityCodes.includes(role)) || 'member'
}

function systemRoles(user: CurrentUser) {
  return displayRoles(user).filter((role) => systemPermissionCodes.includes(role))
}

function isStudentRole(user: CurrentUser) {
  return ['master', 'phd'].includes(schoolIdentity(user))
}

function assignableRoles(user: CurrentUser) {
  const existing = new Set(systemRoles(user))
  return systemPermissionRoles.value.filter((role) => !existing.has(role.code))
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
  accountForm.role_type = 'member'
  accountForm.is_approved = true
  accountForm.is_active = true
  accountForm.system_roles = []
  accountForm.phone = ''
}

function openCreateDrawer() {
  resetAccountForm()
  accountDrawerVisible.value = true
}

function openEditDrawer(user: CurrentUser) {
  editingUserId.value = user.id
  accountForm.real_name = displayUser(user)
  accountForm.email = user.email || ''
  accountForm.username = user.username || ''
  accountForm.password = ''
  accountForm.role_type = schoolIdentity(user)
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
      const previousIdentity = currentUser ? schoolIdentity(currentUser) : 'member'
      const previousSystemRoles = currentUser ? systemRoles(currentUser) : []
      await updateUser(editingUserId.value, {
        email: accountForm.email.trim(),
        username: accountForm.username.trim(),
        real_name: accountForm.real_name.trim(),
        phone: accountForm.phone.trim(),
        role_type: accountForm.role_type,
        is_approved: accountForm.is_approved,
        is_active: accountForm.is_active,
      })
      if (currentUser && previousIdentity !== accountForm.role_type && currentUser.roles.includes(previousIdentity)) {
        await removeUserRole(editingUserId.value, previousIdentity)
      }
      await assignUserRole(editingUserId.value, accountForm.role_type)
      const nextSystemRoles = new Set(accountForm.system_roles)
      await Promise.all(previousSystemRoles.filter((role) => !nextSystemRoles.has(role)).map((role) => removeUserRole(editingUserId.value!, role)))
      await Promise.all(accountForm.system_roles.filter((role) => !previousSystemRoles.includes(role)).map((role) => assignUserRole(editingUserId.value!, role)))
      ElMessage.success('成员账号已保存。')
    } else {
      await createUser({
        email: accountForm.email.trim(),
        username: accountForm.username.trim(),
        password: accountForm.password,
        real_name: accountForm.real_name.trim(),
        phone: accountForm.phone.trim(),
        role_type: accountForm.role_type,
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
  } catch (error: any) {
    users.value = []
    pendingUsers.value = []
    roles.value = []
    studentProfiles.value = []
    errorMessage.value =
      error?.response?.status === 403
        ? '当前账号没有成员管理权限，请使用系统管理员或硕博导师账号访问。'
        : '成员数据加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

async function handleApprove(user: CurrentUser) {
  savingId.value = user.id
  try {
    const identity = schoolIdentityForms[user.id] || 'member'
    await approveUser(user.id, { is_approved: true, role_type: identity })
    await assignUserRole(user.id, identity)
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
    await approveUser(user.id, { is_approved: false, role_type: schoolIdentityForms[user.id] || 'member' })
    ElMessage.success('账号已标记为暂不通过。')
    await reload()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '操作失败，请稍后重试。')
  } finally {
    savingId.value = null
  }
}

async function saveSchoolIdentity(user: CurrentUser) {
  savingId.value = user.id
  try {
    const nextIdentity = schoolIdentityForms[user.id] || 'member'
    const previousIdentity = schoolIdentity(user)
    await approveUser(user.id, { is_approved: Boolean(user.profile?.is_approved), role_type: nextIdentity })
    if (previousIdentity !== nextIdentity && user.roles.includes(previousIdentity)) {
      await removeUserRole(user.id, previousIdentity)
    }
    await assignUserRole(user.id, nextIdentity)
    ElMessage.success('学校身份已保存。')
    await reload()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '学校身份保存失败。')
  } finally {
    savingId.value = null
  }
}

async function handleAssign(user: CurrentUser) {
  const role = assignRoles[user.id]
  if (!role) {
    ElMessage.warning('请选择要添加的系统权限。')
    return
  }
  savingId.value = user.id
  try {
    await assignUserRole(user.id, role)
    assignRoles[user.id] = ''
    ElMessage.success('系统权限已添加。')
    await reload()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '系统权限添加失败，请稍后重试。')
  } finally {
    savingId.value = null
  }
}

async function handleRemoveRole(user: CurrentUser, role: string) {
  if (user.is_superuser) {
    ElMessage.warning('超级管理员权限由系统账号授予，不能在这里移除。')
    return
  }
  if (user.id === session.user?.id && role === 'admin') {
    ElMessage.warning('不能移除自己的系统管理员角色。')
    return
  }
  savingId.value = user.id
  try {
    await removeUserRole(user.id, role)
    ElMessage.success('系统权限已移除。')
    await reload()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '系统权限移除失败。')
  } finally {
    savingId.value = null
  }
}

onMounted(reload)
</script>

<style scoped>
.member-page {
  display: grid;
  gap: 20px;
}

.member-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
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

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  padding: 18px 20px;
}

.stat-card:hover,
.panel:hover {
  transform: none;
}

.stat-card span {
  display: block;
  color: var(--color-muted);
  font-size: 14px;
}

.stat-card strong {
  display: block;
  margin-top: 6px;
  color: var(--color-deep-green);
  font-size: 28px;
  font-weight: 650;
}

.member-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 18px;
}

.panel {
  padding: 24px;
  border-radius: var(--radius-lg);
}

.permission-note {
  align-content: start;
  min-height: 0;
}

.permission-note strong {
  display: block;
  color: var(--color-deep-green);
  font-size: 20px;
  font-weight: 650;
}

.permission-note p {
  margin: 8px 0 0;
  color: var(--color-muted);
  line-height: 1.7;
}

.permission-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 14px;
}

.permission-summary span {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 9px 10px;
  background: #fff;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.55;
}

.permission-summary b {
  display: block;
  color: var(--color-deep-green);
  font-size: 14px;
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
.member-cell small,
.empty-note {
  margin: 4px 0 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

.review-list,
.review-card,
.permission-note {
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

.account-panel {
  overflow: hidden;
}

.account-toolbar {
  align-items: center;
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
  grid-template-columns: minmax(190px, 1.15fr) minmax(210px, 1.25fr) minmax(150px, 1fr) 110px 220px;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  background: var(--color-panel);
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
  border: 1px solid rgba(0, 135, 60, 0.18);
  border-radius: 999px;
  padding: 5px 10px;
  background: var(--color-eco-green);
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.empty-note {
  padding: 14px 0 2px;
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

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.password-alert {
  margin-bottom: 16px;
}

@media (max-width: 1180px) {
  .account-row-card {
    grid-template-columns: 1fr;
  }

  .account-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 980px) {
  .member-heading,
  .account-toolbar {
    display: grid;
  }

  .stat-grid,
  .member-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 720px) {
  .stat-grid,
  .member-grid,
  .review-card {
    grid-template-columns: 1fr;
  }

  .heading-actions,
  .filters {
    justify-content: flex-start;
  }
}
</style>
